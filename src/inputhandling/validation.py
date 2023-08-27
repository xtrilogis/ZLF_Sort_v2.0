"""Contains all methods for validation input"""
import os
from pathlib import Path

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
