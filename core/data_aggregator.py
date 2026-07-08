import pandas as pd
pd.options.future.infer_string = False


def aggregate_emissions(data: pd.DataFrame, group_by: str = "project") -> pd.DataFrame:
    df = data.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    if group_by == "project":
        group_key = "project"
    elif group_by == "file_path":
        group_key = "file_path"
    elif group_by == "hour":
        df["time_group"] = df["timestamp"].dt.floor('h').astype(str)
        group_key = "time_group"
    elif group_by == "day":
        df["time_group"] = df["timestamp"].dt.date.astype(str)
        group_key = "time_group"
    elif group_by == "week":
        df["time_group"] = df["timestamp"].dt.to_period('W').astype(str)
        group_key = "time_group"
    elif group_by == "month":
        df["time_group"] = df["timestamp"].dt.to_period('M').astype(str)
        group_key = "time_group"
    elif group_by == "quarter":
        df["time_group"] = df["timestamp"].dt.to_period('Q').astype(str)
        group_key = "time_group"
    elif group_by == "year":
        df["time_group"] = df["timestamp"].dt.to_period('Y').astype(str)
        group_key = "time_group"
    else:
        print(f"Unsupported aggregation dimension: {group_by}")
    
    agg_columns = {'emissions': ['sum', 'mean']}
    if 'energy_consumption' in df.columns:
        agg_columns['energy_consumption'] = ['sum', 'mean']
    
    result = df.groupby(group_key).agg(agg_columns).reset_index()
    
    if 'energy_consumption' in df.columns:
        result.columns = [group_key, 'total_emissions', 'avg_emissions', 'total_energy', 'avg_energy']
    else:
        result.columns = [group_key, 'total_emissions', 'avg_emissions']
    
    from .database import sanitize_dataframe
    return sanitize_dataframe(result)