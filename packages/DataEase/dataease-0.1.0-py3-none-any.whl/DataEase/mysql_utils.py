import pandas as pd
import sqlalchemy

def connect_to_mysql(user, password, host, db, port=3306):
    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
    return sqlalchemy.create_engine(url)

def create_table_if_not_exists(engine, table_name, df):
    df.head(0).to_sql(table_name, con=engine, if_exists='append', index=False)

def append_df_to_table(engine, table_name, df):
    df.to_sql(table_name, con=engine, if_exists='append', index=False)
