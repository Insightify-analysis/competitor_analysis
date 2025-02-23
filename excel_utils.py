import pandas as pd
from typing import List


def read_excel_to_df(file_path: str, sheet_name: str = None) -> pd.DataFrame:
    return pd.read_excel(file_path, sheet_name=sheet_name)


def load_companies_from_excel(
    file_path: str, sheet_name: str = None, column: str = "Company"
) -> List[str]:
    df = read_excel_to_df(file_path, sheet_name)
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in Excel file.")
    return df[column].dropna().tolist()


def load_companies_from_file(file_path: str, column: str = "Company") -> List[str]:
    if file_path.lower().endswith((".xlsx", ".xls")):
        df = read_excel_to_df(file_path)
    elif file_path.lower().endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Use .xlsx, .xls, or .csv.")
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in the file.")
    return df[column].dropna().tolist()
