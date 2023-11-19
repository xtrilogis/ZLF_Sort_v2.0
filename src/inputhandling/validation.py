"""Contains all methods for validation input"""
from datetime import datetime
from pathlib import Path
from typing import List
import pandas as pd

from assethandling.basemodels import RawTabInput
from assets import constants
from excel.excelmethods import load_sheets_as_df


def is_valid_folder(element: Path) -> bool:
    return element.exists() and element.is_dir() and not element.drive == ""


def validate_excel_file(excel_file: Path):
    """Raises a ValueError, if there is a problem with the excel-file"""
    if not excel_file.exists():
        raise ValueError("Bitte gültige Excel angeben.")
    errors: List[str] = []
    sheets = load_sheets_as_df(excel_file)
    if "Videos" not in sheets.keys():
        errors.append("Excel Mappe 'Videos' fehlt.")
    if "Bilder" not in sheets.keys():
        errors.append("Excel Mappe 'Bilder' fehlt.")
    if "Videos" in sheets.keys() and "Bilder" in sheets.keys():
        result = _validate_sheet(sheets["Videos"])
        if result:
            errors.append("Fehler mit 'Videos' Mappe")
            errors.extend(result)
        result = _validate_sheet(sheets["Bilder"])
        if result:
            errors.append("Fehler mit 'Bilder' Mappe")
            errors.extend(result)
    if errors:
        raise ValueError("\n".join(errors))


def _validate_sheet(df: pd.DataFrame) -> List[str]:
    errors = []

    for column in constants.minimal_columns:
        if column not in df.columns:
            errors.append(f"Spalte {column} fehlt.")
    if True in set(df['Datei'].duplicated()):
        errors.append("Folgende Datei Namen sind doppelt, bitte ändere das manuell")
        errors.extend(df[df['Datei'].duplicated()]["Datei"].tolist())

    return errors


def validate_setup_path(path: Path):
    """Validates input for setting up the folders
    :arg path
    """
    if not is_valid_folder(path):
        raise ValueError("Der angegebene Pfad ist kein valider Ordnerpfad.")
    if "Rohmaterial" in path.as_uri():
        raise ValueError("Der Pfad enthält das Wort 'Rohmaterial'.\n"
                         "Dies kann später zu Problemen führen.\n"
                         "Bitte Ändern!")


def validate_raw(inputs: RawTabInput):
    errors = []
    if not is_valid_folder(inputs.raw_material_folder):
        errors.append("Bitte einen gültigen Rohmaterialordner angeben.")
    if inputs.do_structure and not isinstance(inputs.first_folder_date, datetime): # isinstance übernimmt pydantic
        errors.append("Bitte ein gültiges Datum angeben, ab dem die Ordner erstellt werden.")
    if inputs.fill_excel:
        validate_excel_file(inputs.excel.full_path)
    if inputs.create_picture_folder and inputs.picture_folder.drive == "":
        errors.append("Bitte eine gültigen Pfad für die Bilder angeben.")
    if errors:
        raise ValueError("\n".join(errors))


def validate_util_paths(raw_material_folder: Path, excel_full_filepath: Path):
    if not is_valid_folder(raw_material_folder):
        raise ValueError("Bitte gib einen gültigen Rohmaterialordner an.")
    validate_excel_file(excel_full_filepath)
