import sqlite3
import pandas as pd

def get_overdue_invoices(db_path="data/invoices.db"):
    """
    Fetch overdue records from SQLite database.
    """
    try:
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM invoices WHERE status = 'OVERDUE'"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_dict(orient='records')
    except Exception as e:
        return {"error": str(e)}
