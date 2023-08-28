from pathlib import Path
from typing import Dict, List

from assets import constants
from excel import excelmethods
import pandas as pd

from fileopertations import file_methods


def prepare_dataframes(excel_file: Path, raw_path: Path) -> Dict[str, pd.DataFrame]:
    sheets = excelmethods.load_sheets_as_df(path=excel_file)
    if sheets["Videos"].empty and sheets["Bilder"].empty:
        raise ValueError("Die Excel enthält keine Daten. Bitte ausfüllen")
    append_file_paths_to_df(sheets=sheets, raw_material_path=raw_path)
    return sheets


def append_file_paths_to_df(sheets: Dict[str, pd.DataFrame], raw_material_path: Path):
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


def copy_section(df: pd.DataFrame, rating) -> List[str]:
    """Iterates through column 'Abschnitt'(Sections), sorts files into given sections
    :arg df pandas DataFrame containing file information
    :arg rating only file with a rating equal or higher will be copied"""
    problems = []
    for count, value in enumerate(df['Abschnitt']):
        if pd.isnull(value):
            continue
        try:
            if df.loc[count, 'Bewertung'] >= rating:
                if pd.isnull(df.loc[count, 'Dateipfad']):
                    raise ValueError(f"Datei konnte nicht kopiert werden: {df.loc[count, 'Datei']}")

                file_fullpath = Path(df.loc[count, 'Dateipfad'])
                destination_folder = get_section_dst_folder(file_fullpath=file_fullpath,
                                                            section=value)
                file_methods.copy_file(src_file=file_fullpath,
                                       dst_folder=destination_folder)
        except (AttributeError, ValueError) as e:
            problems.append(str(e))
        except FileNotFoundError:
            problems.append(f"Datei nicht gefunden: {df.loc[count, 'Datei']}")
    return problems


def get_section_dst_folder(file_fullpath: Path, section: str) -> Path:
    new_parts = []
    for _, part in enumerate(file_fullpath.parent.parts):
        if part == "Rohmaterial":
            part = "Schnittmaterial"
        new_parts.append(part)
    destination = Path(*new_parts) / section
    if not destination.exists():
        destination.mkdir(parents=True)
    return destination


def copy_selections(df: pd.DataFrame, raw_path: Path, columns: List[str], marker: str):
    problems = []
    dst_folder = raw_path.parent / "Schnittmaterial" / "Selektionen"
    for column in columns:

        # -
        if column in df.columns:
            current_folder = dst_folder / column

            for count, value in enumerate(df[column]):
                if pd.isnull(value):
                    pass
                elif marker in value:
                    if pd.isnull(df.loc[count, 'Dateipfad']):
                        problems.append(f"Datei konnte nicht kopiert werden: {df.loc[count, 'Datei']}")
                        continue
                    file_fullpath = df.loc[count, "Dateipfad"]

                    file_methods.copy_file(src_file=file_fullpath,
                                           dst_folder=current_folder)
    return problems
