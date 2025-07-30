import pandas as pd
import os
from DataEase import converter

def test_csv_conversion(tmp_path):
    path = tmp_path / "test.csv"
    df = pd.DataFrame({"A": [1, 2], "B": ["x", "y"]})
    converter.df_to_csv(df, path)
    df_loaded = converter.csv_to_df(path)
    assert df.equals(df_loaded)

def test_json_conversion(tmp_path):
    path = tmp_path / "test.json"
    df = pd.DataFrame([{"A": 1, "B": "x"}, {"A": 2, "B": "y"}])
    converter.df_to_json(df, path)
    df_loaded = converter.json_to_df(path)
    assert df.shape == df_loaded.shape
