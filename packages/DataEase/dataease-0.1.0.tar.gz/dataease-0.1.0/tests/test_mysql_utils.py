import pytest
import pandas as pd
import sqlalchemy
from sqlalchemy import text
from DataEase import mysql_utils

# ✅ Fixture for SQLAlchemy engine
@pytest.fixture(scope="module")
def engine():
    try:
        print("📡 Connecting to MySQL server at localhost:3306...")
        raw_engine = sqlalchemy.create_engine("mysql+pymysql://root:1234@localhost:3306")
        with raw_engine.connect() as conn:
            print("✅ Connected to server. Creating testdb if not exists...")
            conn.execute(text("CREATE DATABASE IF NOT EXISTS testdb"))

        print("🔁 Connecting to testdb using mysql_utils...")
        final_engine = mysql_utils.connect_to_mysql("root", "1234", "localhost", "testdb")

        with final_engine.connect() as conn:
            print("🎉 MySQL Utils test DB connection successful.")

        return final_engine

    except Exception as e:
        print("❌ test_mysql_utils.py skipped: ", e)
        pytest.skip(f"Cannot connect or create MySQL DB: {e}")

# ✅ Sample DataFrame fixture
@pytest.fixture
def sample_df():
    return pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})

# ✅ Your test function
def test_create_and_append(engine, sample_df):
    table_name = "test_table"

    with engine.connect() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))

    # Create table using mysql_utils
    mysql_utils.create_table_if_not_exists(engine, table_name, sample_df)
    mysql_utils.append_df_to_table(engine, table_name, sample_df)

    # Verify insertion
    from DataEase import sql_utils
    results = sql_utils.run_query(engine, f"SELECT * FROM {table_name}")
    assert len(results) == 2
