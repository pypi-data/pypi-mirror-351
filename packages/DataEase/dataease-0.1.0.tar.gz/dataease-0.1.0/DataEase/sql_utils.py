from sqlalchemy import text

def run_query(engine, query):
    """
    Runs a raw SQL query and returns fetched results if applicable.
    For SELECT queries: returns result rows.
    For INSERT/CREATE/DROP: returns None.
    """
    with engine.connect() as conn:
        result = conn.execute(text(query))
        try:
            return result.fetchall()
        except Exception:
            return None

def insert_row(engine, table_name, data: dict):
    """
    Inserts a single row (dict) into the specified table.
    Uses SQLAlchemy's text binding with transaction support.
    """
    keys = ", ".join(data.keys())
    values = ", ".join([f":{key}" for key in data.keys()])
    query = text(f"INSERT INTO {table_name} ({keys}) VALUES ({values})")

    with engine.begin() as conn:  # ✅ ensures transaction is committed
        conn.execute(query, data)
