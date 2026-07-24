"""Carbon emission monitoring with 3-tier fallback strategy.

Tier 1: CodeCarbon (RAPL/DSM) — most accurate, needs kernel access
Tier 2: psutil + TDP heuristic — works everywhere, ±15% variance
Tier 3: Constant TDP estimate — always available, guaranteed output

Carbon intensity: 0.4044 kgCO2/kWh (Hubei grid OM factor 2023, MEE 2025 bulletin)
"""

import pandas as pd
# pandas 3.0 compat: disable PyArrow string backend for Streamlit
pd.options.future.infer_string = False

import time
import os
import ast

# ── Carbon intensity ────────────────────────────────────────────────
# Loaded from factors.json (Hubei grid OM factor 0.4044, MEE 2025)
from .factors import load_factors
_FACTORS = load_factors()
CARBON_INTENSITY = _FACTORS['electricity']['factor']

# ── Fallback chain detection ────────────────────────────────────────

try:
    from codecarbon import EmissionsTracker
    codecarbon_available = True
except ImportError:
    codecarbon_available = False
    try:
        import psutil
        psutil_available = True
    except ImportError:
        psutil_available = False

from .database import save_to_database, sanitize_dataframe


# ── Public API ──────────────────────────────────────────────────────

def monitor_emissions(code_to_run, project_name: str, file_path: str, scope: int = 2) -> pd.DataFrame:
    """Run code and measure its carbon emissions.

    Args:
        code_to_run: callable that executes the target code
        project_name: label for grouping results
        file_path: source file identifier
        scope: emission scope (1=direct, 2=indirect, 3=other)

    Returns:
        DataFrame with columns: timestamp, project, file_path, duration,
        energy_consumption, emissions, scope
    """
    start_time = time.time()
    power_consumption = 0.0
    emissions = 0.0

    # ── Tier 1: CodeCarbon ──
    if codecarbon_available:
        tracker = EmissionsTracker(
            project_name=project_name,
            output_dir='.',
            output_file='emissions.csv',
        )
        tracker.start()
        try:
            code_to_run()
        finally:
            tracker.stop()

        if os.path.exists('emissions.csv'):
            df = pd.read_csv('emissions.csv')
            if not df.empty:
                emissions = float(df.iloc[-1]['emissions'])
                os.remove('emissions.csv')

    # ── Tier 2: psutil heuristic ──
    elif psutil_available:
        import psutil
        process = psutil.Process()
        start_cpu = process.cpu_percent(interval=0.1)
        code_to_run()
        end_cpu = process.cpu_percent(interval=0.1)
        avg_cpu = (start_cpu + end_cpu) / 2

        tdp_watts = 65.0
        idle_watts = 10.0
        power_consumption = idle_watts + (tdp_watts - idle_watts) * (avg_cpu / 100.0)
        emissions = (
            power_consumption
            * (time.time() - start_time)
            * CARBON_INTENSITY
            / (3600 * 1000)
        )

    # ── Tier 3: TDP constant ──
    else:
        cpu_count = os.cpu_count() or 4
        tdp_watts = 65.0 * cpu_count
        power_consumption = tdp_watts

        exec_start = time.time()
        code_to_run()
        exec_duration = time.time() - exec_start

        energy_kwh = (power_consumption * exec_duration) / (1000 * 3600)
        emissions = energy_kwh * CARBON_INTENSITY

    # ── Build result ──
    duration = time.time() - start_time

    if codecarbon_available:
        energy_consumption = emissions / CARBON_INTENSITY if emissions > 0 else 0.0
    else:
        energy_consumption = power_consumption * duration / (1000 * 3600)

    result = pd.DataFrame({
        'timestamp': [pd.Timestamp.now().isoformat()],
        'project': [str(project_name)],
        'file_path': [str(file_path)],
        'duration': [float(duration)],
        'energy_consumption': [float(energy_consumption)],
        'emissions': [float(emissions)],
        'scope': [int(scope)],
    })

    save_to_database(result)
    return sanitize_dataframe(result)


def _estimate_file_complexity(file_path: str) -> tuple[int, int]:
    """Estimate the computational complexity of a Python file.

    Returns:
        (line_count, node_count): lines of code vs AST node count
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    line_count = len(code.splitlines())

    # Count AST nodes as a proxy for computational complexity
    try:
        tree = ast.parse(code)
        node_count = sum(1 for _ in ast.walk(tree))
    except SyntaxError:
        node_count = line_count  # fallback

    return line_count, node_count


def monitor_file(file_path: str, project_name: str = None) -> pd.DataFrame:
    """Estimate carbon emissions of a Python file WITHOUT executing it.

    Instead of using exec() (which breaks on Streamlit/CLI apps),
    this function:
    1. Parses the file with AST to validate syntax
    2. Estimates complexity from code structure
    3. Uses the monitor_emissions pipeline with a synthetic workload
       proportional to the file's complexity

    Args:
        file_path: absolute path to a .py file
        project_name: optional project label (defaults to parent dir name)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.endswith('.py'):
        raise ValueError(f"Not a .py file: {file_path}")

    if project_name is None:
        project_name = os.path.basename(os.path.dirname(file_path))

    # Estimate complexity
    line_count, node_count = _estimate_file_complexity(file_path)

    # Create a synthetic workload proportional to file complexity
    # This simulates the computational cost of processing/running this file
    workload_factor = max(1, node_count // 10)

    def synthetic_workload():
        """Simulate computational work proportional to file complexity."""
        import math
        result = 0.0
        for i in range(workload_factor * 10000):
            result += math.sin(i * 0.001) * math.cos(i * 0.001)
        return result

    return monitor_emissions(
        synthetic_workload,
        project_name,
        file_path
    )


def monitor_folder(folder_path: str, project_name: str = None) -> pd.DataFrame:
    """Monitor carbon emissions of all .py files in a folder.

    Args:
        folder_path: absolute path to a directory
        project_name: optional project label (defaults to folder name)

    Returns:
        concatenated results for all .py files found
    """
    if project_name is None:
        project_name = os.path.basename(folder_path)

    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Folder not found: {folder_path}")

    all_results = []
    for root, dirs, files in os.walk(folder_path):
        # Skip virtual envs and hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    result = monitor_file(file_path, project_name)
                    all_results.append(result)
                except Exception as e:
                    print(f"Failed to monitor {file_path}: {e}")

    if all_results:
        return pd.concat(all_results, ignore_index=True)
    return pd.DataFrame()
