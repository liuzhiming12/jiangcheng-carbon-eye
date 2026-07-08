import sqlite3
import pandas as pd
pd.options.future.infer_string = False


def sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Convert PyArrow-backed columns to standard types for Streamlit compatibility.

    Streamlit's Arrow serialization does not recognize PyArrow dtypes like
    ``LargeUtf8``. This function converts all Arrow-backed and extension
    dtypes to plain numpy/object types.
    """
    df = df.copy()
    for col in df.columns:
        dtype = df[col].dtype
        # Check for PyArrow / extension types (pandas 3.0 uses Arrow by default)
        if (
            isinstance(dtype, pd.ArrowDtype)
            or hasattr(dtype, 'pyarrow_dtype')
            or 'arrow' in str(dtype).lower()
        ):
            df[col] = df[col].astype(object)
    return df

def init_database(db_path: str = "carbon_data.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS emissions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        project TEXT,
        file_path TEXT,
        duration REAL,
        energy_consumption REAL,
        emissions REAL,
        scope INTEGER
    )
    ''')
    conn.commit()
    conn.close()

def save_to_database(data: pd.DataFrame, db_path: str = "carbon_data.db"):
    init_database(db_path)
    
    allowed_columns = ['timestamp', 'project', 'file_path', 'duration', 'energy_consumption', 'emissions', 'scope']
    data = data[allowed_columns].copy()
    
    for col in data.columns:
        if str(data[col].dtype).startswith('Large') or str(data[col].dtype) == 'string':
            data[col] = data[col].astype(object)
    
    data['timestamp'] = data['timestamp'].astype(str)
    
    conn = sqlite3.connect(db_path)
    data.to_sql('emissions', conn, if_exists = 'append', index = False)
    conn.close()

def load_from_database(db_path: str = "carbon_data.db") -> pd.DataFrame:
    init_database(db_path)
    conn = sqlite3.connect(db_path)
    data = pd.read_sql('SELECT * FROM emissions', conn)
    conn.close()
    
    for col in data.columns:
        if str(data[col].dtype).startswith('Large') or str(data[col].dtype) == 'string':
            data[col] = data[col].astype(object)
    
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data['duration'] = data['duration'].astype(float)
    data['energy_consumption'] = data['energy_consumption'].astype(float)
    data['emissions'] = data['emissions'].astype(float)
    data['scope'] = data['scope'].astype(int)
    
    return data

def get_projects(db_path: str = "carbon_data.db") -> list:
    init_database(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT project FROM emissions')
    projects = [row[0] for row in cursor.fetchall()]
    conn.close()
    return projects