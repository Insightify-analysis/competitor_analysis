import pandas as pd
from wiki.excel_utils import read_excel_to_df


def read_excel_to_df(file_path: str, sheet_name: str = None) -> pd.DataFrame:
    """
    Reads an Excel file into a pandas DataFrame.
    """
    return pd.read_excel(file_path, sheet_name=sheet_name)
