import os.path
from pathlib import Path
from typing import List, Dict

import pandas as pd
from pandas import DataFrame

from assethandling.basemodels import SheetConfig


def create_emtpy_excel(file_name, path, sheets: List[SheetConfig], override=False):
    """Creates a new Excel file, at the given path, with the given sheets
    :raise FileExistsError, if the there already is a file with the same name
    :param file_name:
    :param path: folder where Excel should be saved
    :param sheets:
    :return:
    """
    if ".xlsx" not in file_name:
        file_name += ".xlsx"
    full_excel_path = os.path.join(path, file_name)
    if os.path.exists(full_excel_path) and not override:
        raise FileExistsError
    else:
        with pd.ExcelWriter(full_excel_path, engine='xlsxwriter') as writer:
            for sheet in sheets:
                df = pd.DataFrame(columns=sheet.columns)
                df.to_excel(writer, index=False, sheet_name=sheet.name)


def save_df_to_excel(df, path):
    pass


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
