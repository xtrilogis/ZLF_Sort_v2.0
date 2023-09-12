from pathlib import Path
from typing import List, Dict

import pandas as pd
from pandas import DataFrame

from assethandling.basemodels import SheetConfig, ExcelConfig


def create_emtpy_excel(config: ExcelConfig, override=False) -> Path:
    """Creates a new Excel file, at the given path, with the given sheets
    :param config:
    :raise FileExistsError, if the there already is a file with the same name
    :param override:
    :return: path to new created
    """
    if ".xlsx" not in config.excel_file_name:
        config.excel_file_name += ".xlsx"
    full_excel_path = config.excel_folder / config.excel_file_name
    if full_excel_path.exists() and not override:
        raise FileExistsError
    else:
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
    return pd.read_excel(path, sheet_name=None)


def get_columns(excel, sheet) -> List[str]:
    """Extracts all columns the given sheet has
        :param excel fullpath of the Excel file
        :param sheet to search"""
    df = pd.read_excel(excel, sheet_name=sheet)
    return df.columns


if __name__ == "__main__":
    create_emtpy_excel("test", "D:/", [SheetConfig(name="sdf", columns=["sae", "eas"])])
