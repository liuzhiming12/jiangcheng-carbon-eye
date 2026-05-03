import sqlite3

def get_emission_trend(db_path="carbon_data.db", days=30):
    """Query daily carbon emission trends for the past N days"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date(timestamp) as day, SUM(emissions) as total
        FROM emissions
        WHERE timestamp >= date('now', '-' || ? || ' days')
        GROUP BY day
        ORDER BY day
    """, (days,))
    rows = cursor.fetchall()
    conn.close()
    return rows