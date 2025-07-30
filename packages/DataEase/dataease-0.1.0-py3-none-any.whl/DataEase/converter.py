import pandas as pd

def df_to_csv(df, path):
    df.to_csv(path, index=False)

def csv_to_df(path):
    return pd.read_csv(path)

def df_to_json(df, path):
    df.to_json(path, orient='records', lines=True)

def json_to_df(path):
    return pd.read_json(path, lines=True)
