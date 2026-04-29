import sqlite3
import pandas as pd

def init_database(db_path: str = "carbon_data.db"):
    """
    Initialize the database with necessary tables
    """
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
    """
    Save emissions data to SQLite database
    """
    init_database(db_path)
    
    # Only keep columns that exist in the database table
    allowed_columns = ['timestamp', 'project', 'file_path', 'duration', 'energy_consumption', 'emissions', 'scope']
    data = data[allowed_columns]
    
    conn = sqlite3.connect(db_path)
    data.to_sql('emissions', conn, if_exists = 'append', index = False)
    conn.close()

def load_from_database(db_path: str = "carbon_data.db") -> pd.DataFrame:
    """
    Load emission data from SQLite database
    """
    init_database(db_path)
    conn = sqlite3.connect(db_path)
    data = pd.read_sql('SELECT * FROM emissions', conn)
    conn.close()
    return data

def get_projects(db_path: str = "carbon_data.db") -> list:
    """
    Get all unique project names from database
    """
    init_database(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT project FROM emissions')
    projects = [row[0] for row in cursor.fetchall()]
    conn.close()
    return projects