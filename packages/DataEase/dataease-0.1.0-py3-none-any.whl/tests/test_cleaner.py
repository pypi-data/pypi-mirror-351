import pandas as pd
from DataEase import cleaner

def test_remove_duplicates():
    df = pd.DataFrame({"A": [1, 1, 2], "B": [3, 3, 4]})
    result = cleaner.remove_duplicates(df)
    assert len(result) == 2

def test_remove_nulls():
    df = pd.DataFrame({"A": [1, None], "B": [2, 3]})
    result = cleaner.remove_nulls(df)
    assert result.isnull().sum().sum() == 0

def test_fill_nulls_mean():
    df = pd.DataFrame({"A": [1.0, None, 3.0]})
    result = cleaner.fill_nulls(df)
    assert result.isnull().sum().sum() == 0

def join_columns(df, cols_to_join, new_col_name, sep="_"):
    if not isinstance(cols_to_join, list):
        raise TypeError("cols_to_join must be a list of column names")
    df[new_col_name] = df[cols_to_join].astype(str).agg(sep.join, axis=1)
    return df



def test_drop_constant_columns():
    df = pd.DataFrame({"A": [1, 1, 1], "B": [1, 2, 3]})
    result = cleaner.drop_constant_columns(df)
    assert "A" not in result.columns

def test_full_clean():
    df = pd.DataFrame({"A": [1, 1, None], "B": [2, 2, 2]})
    result = cleaner.full_clean(df)
    assert result.isnull().sum().sum() == 0
