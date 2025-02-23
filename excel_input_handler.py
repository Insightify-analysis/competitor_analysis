import pandas as pd

# Updated import statement with alias:
from wiki.excel_utils import (
    load_companies_from_excel as utils_load_companies_from_excel,
)


# Renamed wrapper function to avoid name collision
def handle_excel_input(
    file_path: str, sheet_name: str = None, column: str = "Company"
) -> list:
    """
    Load company names from an Excel file.
    Expects a column with header 'Company' by default.
    """
    return utils_load_companies_from_excel(file_path, sheet_name, column)
