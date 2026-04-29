import pandas as pd
import time
import os

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

def monitor_emissions(code_to_run, project_name: str, file_path : str, scope: int = 2) -> pd.DataFrame:
    """
    Monitor carbon emissions during code execution

    Args:
    code_to_run - Function to execute
    project_name: str - Project name
    file_path: str - File path
    scope: int - Emission scope (1: direct, 2: indirect, 3: other indirect)

    Returns:
    pd.DataFrame - Emission data with timestamp, project, file_path, duration, energy_consumption, emissions, scope
    """
    start_time = time.time()
    if codecarbon_available:
        tracker = EmissionsTracker(project_name = project_name, output_dir = '.', output_file = 'emissions.csv')
        tracker.start()
        try:
            code_to_run()
        finally:
            tracker.stop()
        if os.path.exists('emissions.csv'):
            df = pd.read_csv('emissions.csv')
            if not df.empty:
                emissions = df.iloc[-1]['emissions']
                os.remove('emissions.csv') 
            else:
                emissions = 0
        else:
            emissions = 0
    elif psutil_available:
        import psutil
        process = psutil.Process()
        start_cpu = process.cpu_percent(interval = 0.1)
        code_to_run()
        end_cpu = process.cpu_percent(interval = 0.1)
        avg_cpu = (start_cpu + end_cpu) / 2
        power_consumption = avg_cpu * 0.1 
        emissions = power_consumption * (time.time() - start_time) * 0.562 / (3600 * 1000)
    else:
        code_to_run()
        emissions = 0
    duration = time.time() - start_time
    # Calculate energy consumption (kWh)
    # For codecarbon, we'll estimate based on emissions and carbon intensity
    # For psutil, we already have power consumption
    if codecarbon_available:
        # Estimate energy consumption from emissions
        energy_consumption = emissions / 0.562 if emissions > 0 else 0
    elif psutil_available:
        # Calculate energy consumption from power and duration
        energy_consumption = power_consumption * duration / (1000 * 3600)
    else:
        energy_consumption = 0
    
    result = pd.DataFrame({
        'timestamp': [pd.Timestamp.now()],
        'project': [project_name],
        'file_path': [file_path],
        'duration': [duration],
        'energy_consumption': [energy_consumption],
        'emissions': [emissions],
        'scope': [scope]
    })
    return result