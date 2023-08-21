import os.path
from typing import List

import pandas as pd
from assethandling.basemodels import SheetConfig


def create_emtpy_excel(file_name, path, sheets: List[SheetConfig]):
    """Creates a new Excel file, at the given path, with the given sheets
    :raise FileExistsError, if the there already is a file with the same name
    :param file_name:
    :param path:
    :param sheets:
    :return:
    """
    if ".xlsx" not in file_name:
        file_name += ".xlsx"
    full_excel_path = os.path.join(path, file_name)
    if os.path.exists(full_excel_path):
        raise FileExistsError
    else:
        with pd.ExcelWriter(full_excel_path, engine='xlsxwriter') as writer:
            for sheet in sheets:
                df = pd.DataFrame(columns=sheet.columns)
                df.to_excel(writer, index=False, sheet_name=sheet.name)


def save_df_to_excel(df, path):
    pass


def load_df_from_excel(path) -> list:
    # liste aller sheets
    pass


if __name__ == "__main__":
    create_emtpy_excel("test", "D:/", [SheetConfig(name="sdf", columns=["sae", "eas"])])
