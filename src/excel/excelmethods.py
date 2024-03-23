from pathlib import Path
from typing import Dict, List

import pandas as pd
from pandas import DataFrame

from assethandling.basemodels import ExcelConfig


def create_emtpy_excel(config: ExcelConfig, override=False) -> Path:
    """Creates a new Excel file, at the given path, with the given sheets
    :param config: _
    :raise FileExistsError, if the there already is a file with the same name
    :param override: _
    :return: path to new created
    """
    if ".xlsx" not in config.excel_file_name:
        config.excel_file_name += ".xlsx"
    full_excel_path = config.excel_folder / config.excel_file_name
    if full_excel_path.exists() and not override:
        raise FileExistsError

    sheets: Dict[str, DataFrame] = {}
    for sheet in config.sheets:
        sheets[sheet.name] = pd.DataFrame(columns=sheet.columns)
    save_sheets_to_excel(sheets=sheets, path=full_excel_path)
    return full_excel_path


def save_sheets_to_excel(sheets: Dict[str, DataFrame], path: Path):
    # with pd.ExcelWriter(full_excel_path, engine='xlsxwriter') as writer:
    with pd.ExcelWriter(path) as writer:
        for key, value in sheets.items():
            sheets[key].to_excel(writer, index=False, sheet_name=key)


def load_sheets_as_df(path: Path) -> Dict[str, DataFrame]:
    """
    Get all sheets from the given Excel and return them in a dictionary
    with the sheet name as key and the DataFrame as value
    :param path: path to the Excel file
    :return: dictionary with all sheets as keys and the DataFrame as value
    """
    return pd.read_excel(path, sheet_name=None)


def get_columns(excel: Path, sheet: str) -> List[str]:
    """Extracts all columns the given sheet has
    :param excel fullpath of the Excel file
    :param sheet to search
    :returns list of column names the given sheet has"""
    df = pd.read_excel(excel, sheet_name=sheet)
    return df.columns
