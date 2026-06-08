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

from .emission_calculator import calculate_emissions


def compare_strategies(code_to_run, iterations=5):
    """
    对比三种监测策略的性能和准确性
    
    Args:
        code_to_run: 要执行的代码函数
        iterations: 迭代次数
    
    Returns:
        pd.DataFrame: 各策略的平均排放量和标准差
    """
    results = []
    strategies = [
        ('codecarbon', _monitor_with_codecarbon),
        ('psutil', _monitor_with_psutil),
        ('tdp', _monitor_with_tdp)
    ]
    
    for _ in range(iterations):
        for name, func in strategies:
            try:
                result = func(code_to_run, "test", "test.py")
                results.append({
                    "strategy": name,
                    "emissions": result['emissions']
                })
            except Exception as e:
                print(f"策略 {name} 失败: {e}")
    
    if not results:
        return None
    
    df = pd.DataFrame(results)
    comparison = df.groupby('strategy')['emissions'].agg(['mean', 'std']).reset_index()
    comparison.columns = ['策略', '平均排放(kgCO2)', '标准差']
    
    return comparison


def _monitor_with_codecarbon(code_to_run, project_name, file_path):
    """使用CodeCarbon监测碳排放"""
    tracker = EmissionsTracker(project_name=project_name, output_dir='.', output_file='emissions.csv')
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
    
    return {'emissions': emissions}


def _monitor_with_psutil(code_to_run, project_name, file_path):
    """使用psutil监测碳排放"""
    import psutil
    process = psutil.Process()
    start_time = time.time()
    
    start_cpu = process.cpu_percent(interval=0.1)
    code_to_run()
    end_cpu = process.cpu_percent(interval=0.1)
    
    avg_cpu = (start_cpu + end_cpu) / 2
    tdp_watts = 65
    idle_watts = 10
    power_consumption = idle_watts + (tdp_watts - idle_watts) * (avg_cpu / 100)
    
    duration = time.time() - start_time
    emissions = power_consumption * duration * 0.4044 / (3600 * 1000)
    
    return {'emissions': emissions}


def _monitor_with_tdp(code_to_run, project_name, file_path):
    """使用TDP估算碳排放"""
    cpu_count = os.cpu_count() or 4
    tdp_watts = 65 * cpu_count
    
    start_time = time.time()
    code_to_run()
    duration = time.time() - start_time
    
    result = calculate_emissions(power_consumption=tdp_watts, duration=duration)
    
    return {'emissions': result['emissions']}

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
    power_consumption = 0
    
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
        # psutil fallback: estimate power from CPU utilization + TDP
        # Assume CPU TDP = 65W, idle = 10W, linear scaling
        tdp_watts = 65
        idle_watts = 10
        power_consumption = idle_watts + (tdp_watts - idle_watts) * (avg_cpu / 100)
        emissions = power_consumption * (time.time() - start_time) * 0.4364 / (3600 * 1000)
    else:
        # TDP-based estimation as ultimate fallback (no psutil available)
        cpu_count = os.cpu_count() or 4
        tdp_watts = 65 * cpu_count
        
        # Measure actual execution time first, then estimate emissions
        execution_start = time.time()
        code_to_run()
        duration = time.time() - execution_start
        
        result = calculate_emissions(power_consumption=tdp_watts, duration=duration)
        emissions = result['emissions']
        power_consumption = tdp_watts
    
    duration = time.time() - start_time
    # Calculate energy consumption (kWh)
    # For codecarbon, we'll estimate based on emissions and carbon intensity
    # For psutil and TDP fallback, we have power consumption
    if codecarbon_available:
        # Estimate energy consumption from emissions
        energy_consumption = emissions / 0.4364 if emissions > 0 else 0
    else:
        # Calculate energy consumption from power and duration
        energy_consumption = power_consumption * duration / (1000 * 3600)
    
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
