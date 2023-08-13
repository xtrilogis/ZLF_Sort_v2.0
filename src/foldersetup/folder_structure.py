import os
from datetime import datetime
import pandas as pd
from PyQt5.QtCore import QDate


def create_folder_structure(parent: str, date: QDate):
    """Creates all necessary folders"""
    root_subfolder = ["Projekte", "Film", "Rohmaterial", "Schnittmaterial", "ext. Material"]
    raw_subfolder = day_folder(date=date)  # Subfolder for 'Rohmaterial'
    ext_m_subfolder = ["Dokumente", "Musik", "Grafiken"]  # Subfolder for 'ext. Material'

    if not os.path.exists(parent):
        os.makedirs(parent)

    for folder in root_subfolder:
        create = os.path.join(parent, folder)
        if not os.path.exists(create):
            os.makedirs(create)

    for folder in raw_subfolder:
        create = os.path.join(parent, "Rohmaterial", folder)
        if not os.path.exists(create):
            os.makedirs(create)

    for folder in ext_m_subfolder:
        create = os.path.join(parent, "ext. Material", folder)
        if not os.path.exists(create):
            os.makedirs(create)


def day_folder(date: QDate):
    """Creates a folder for every day with subfolders 'Bilder' and 'Videos'"""
    letter = 97  # kleines a
    days = ["Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag", "Montag", "Dienstag"]
    day_folders = []
    for i in range(10):
        # ggf. Datum automatisch ausfüllen
        day_folders.append(f'{chr(letter + i)}-Datum-{days[i % 7]}/Bilder')
        day_folders.append(f'{chr(letter + i)}-Datum-{days[i % 7]}/Videos')
    return day_folders
