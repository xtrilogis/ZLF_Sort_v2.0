from pathlib import Path
from plistlib import Dict

from assets import constants
from excel import excelmethods
import pandas as pd


def prepare_dataframes(excel_file: Path, raw_path: Path) -> dict[str, pd.DataFrame]:
    sheets = excelmethods.load_sheets_as_df(path=excel_file)
    append_file_paths_to_df(sheets=sheets, raw_material_path=raw_path)
    return sheets


def append_file_paths_to_df(sheets: dict[str, pd.DataFrame], raw_material_path: Path):
    """Creates a new column 'Dateipfad' and fills it with the files fullpath
    :arg sheets pandas DataFrames with the all files and the markers
    :arg raw_material_path
    :returns df with new filled column 'Dateipfad' (eng. 'filepath') """
    sheets["Videos"]["Dateipfad"] = pd.Series(dtype='str')
    sheets["Bilder"]["Dateipfad"] = pd.Series(dtype='str')
    for element in raw_material_path.glob('**/*'):
        if element.is_file():
            if element.suffix in constants.video_extensions:
                df = sheets["Videos"]
            elif element.suffix in constants.image_extensions:
                df = sheets["Bilder"]
            else:
                continue

            match = df.loc[df['Datei'] == element.name]
            if not match.empty:
                row = match.index[0]
                df.loc[row, "Dateipfad"] = element
