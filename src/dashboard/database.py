import pandas as pd
import psycopg2

def get_db_connection():
    """Get PostgreSQL database connection."""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="root",
        database="kcartbot"
    )

def execute_query(query, params=None):
    """Execute a database query and return results."""
    conn = get_db_connection()
    try:
        if params:
            result = pd.read_sql_query(query, conn, params=params)
        else:
            result = pd.read_sql_query(query, conn)
        return result
    except Exception as e:
        from streamlit import error
        error(f"Database error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()