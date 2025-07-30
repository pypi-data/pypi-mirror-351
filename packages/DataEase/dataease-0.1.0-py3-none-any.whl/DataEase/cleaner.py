import pandas as pd

def remove_duplicates(df):
    return df.drop_duplicates()

def remove_nulls(df):
    return df.dropna()

def fill_nulls(df, method='mean'):
    for col in df.select_dtypes(include='number'):
        if method == 'mean':
            df[col] = df[col].fillna(df[col].mean())
        elif method == 'median':
            df[col] = df[col].fillna(df[col].median())
    return df

def join_columns(df, cols_to_join, new_col_name, sep=" "):
    df[new_col_name] = df[cols_to_join].astype(str).agg(sep.join, axis=1)
    return df


def drop_constant_columns(df):
    return df.loc[:, df.nunique() > 1]

def convert_dtypes(df):
    return df.convert_dtypes()

def full_clean(df):
    df = remove_duplicates(df)
    df = drop_constant_columns(df)
    df = fill_nulls(df, method='mean')
    df = convert_dtypes(df)
    return df
