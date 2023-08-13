"""Contains all methods for validation input"""
import os
import pandas as pd
from PyQt5.QtCore import QDate


def validate_setup(harddrive: str, date: QDate):
    """Validates input for setting up the folders
    :arg harddrive
    :arg date
    """
    if not date.isValid():
        return False, "Kein valides Datum."
    if os.path.exists(harddrive) and os.path.isdir(harddrive):
        if "Rohmaterial" in harddrive:
            return False, "Der Pfad enthält das Wort 'Rohmaterial'.\n" \
                          "Dies kann später zu Problemen führen.\n" \
                          "Bitte Ändern!"
        return True, ""
    return False, "Der angegebene Pfad ist kein valider Ordnerpfad."
