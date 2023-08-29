"""Contains all methods for validation input"""
from pathlib import Path
from typing import Tuple, List
import pandas as pd

from assets import constants
from excel import excelmethods


def validate_setup_path(path: Path):
    """Validates input for setting up the folders
    :arg path
    """
    if path.exists() and path.is_dir():
        if "Rohmaterial" in path.as_uri():
            return False, "Der Pfad enthält das Wort 'Rohmaterial'.\n" \
                          "Dies kann später zu Problemen führen.\n" \
                          "Bitte Ändern!"
        return True, ""
    return False, "Der angegebene Pfad ist kein valider Ordnerpfad."


def _validate_excel_file(excel_file: Path) -> List[str]:
    errors: List[str] = []
    try:
        sheets = excelmethods.load_sheets_as_df(excel_file)
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
                errors.append("Fehler mit 'Videos' Mappe")
                errors.extend(result)
    except Exception as e:
        return [str(e)]

    return errors


def _validate_sheet(df: pd.DataFrame) -> List[str]:
    errors = []

    for column in constants.minimal_columns:
        if column not in df.columns:
            errors.append(f"Spalte {column} fehlt.")
    if True in set(df['Datei'].duplicated()):
        errors.append("folgende Datei Namen sind doppelt, bitte ändere das manuell")
        errors.extend(df[df['Datei'].duplicated()]["Datei"].tolist())

    return errors


def validate_util_paths(raw_material_folder: Path, excel_full_filepath: Path) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if not raw_material_folder.exists():
        errors.append("Bitte gib einen gültigen Rohmaterialordner an.")
    elif not raw_material_folder.is_dir():
        errors.append("Bitte gib einen gültigen Rohmaterialordner an.")

    if not excel_full_filepath.exists():
        errors.append("Bitte gib eine gültige Exceldatei an.")
    else:
        errors.extend(_validate_excel_file(excel_full_filepath))

    return len(errors) == 0, errors
