import pytest
from DataEase import sql_utils, mysql_utils
import sqlalchemy
import pymysql
from sqlalchemy import text

@pytest.fixture(scope="module")
def engine():
    try:
        print("📡 Connecting to MySQL server at localhost:3306...")
        raw_engine = sqlalchemy.create_engine("mysql+pymysql://root:1234@localhost:3306")
        with raw_engine.connect() as conn:
            print("✅ Connected to server. Creating testdb if not exists...")
            conn.execute(text("CREATE DATABASE IF NOT EXISTS testdb"))

        print("🔁 Connecting to testdb...")
        final_engine = mysql_utils.connect_to_mysql("root", "1234", "localhost", "testdb")
        with final_engine.connect() as conn:
            print("🎉 Successfully connected to testdb and ready to run tests.")
        return final_engine

    except Exception as e:
        print("❌ SKIPPED due to MySQL connection error:")
        print(e)
        pytest.skip(f"Cannot connect or create MySQL DB: {e}")


def test_run_query_and_insert(engine):
    table_name = "test_insert"
    sql_utils.run_query(engine, f"DROP TABLE IF EXISTS {table_name}")
    sql_utils.run_query(engine, f"CREATE TABLE {table_name} (id INT, name VARCHAR(50))")

    sql_utils.insert_row(engine, table_name, {"id": 1, "name": "TestUser"})
    results = sql_utils.run_query(engine, f"SELECT * FROM {table_name}")
    assert results[0][0] == 1
    assert results[0][1] == "TestUser"
