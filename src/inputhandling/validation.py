"""Contains all methods for validation input"""
import os
from pathlib import Path
from typing import Tuple

import pandas as pd
from datetime import datetime


def validate_setup(harddrive: Path, date: datetime):
    """Validates input for setting up the folders
    :arg harddrive
    :arg date
    """
    if harddrive.exists() and harddrive.is_dir():
        if "Rohmaterial" in harddrive.as_uri():
            return False, "Der Pfad enthält das Wort 'Rohmaterial'.\n" \
                          "Dies kann später zu Problemen führen.\n" \
                          "Bitte Ändern!"
        return True, ""
    return False, "Der angegebene Pfad ist kein valider Ordnerpfad."


def validate_excel_file(excel_file: Path):
    # TODO
    # exists
    # Bilder und Videos !!!
    # check for double Filenames
    # Spalten Name, Abschnitt, Bewertung
    # empty wird wo anders geprüft
    pass


def validate_util() -> Tuple[bool, str]:
    # TODO
    # check if excel and raw correct
    return True, ""
