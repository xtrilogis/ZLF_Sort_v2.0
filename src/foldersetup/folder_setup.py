import locale
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from fileopertations.filemethods import create_folder

locale.setlocale(locale.LC_TIME, "de_DE.utf8")


def create_folder_structure(parent: Path, date: datetime):
    """Creates all necessary folders"""
    root_subfolder = [
        "Projekte",
        "Film",
        "Rohmaterial",
        "Schnittmaterial",
        "ext. Material",
    ]

    ext_m_subfolder = [
        "Dokumente",
        "Musik",
        "Grafiken",
    ]  # Subfolder for 'ext. Material'

    parent = create_folder(parent=parent, folder=f"Zeltlagerfilm {date.year}")

    for folder in root_subfolder:
        create_folder(parent=parent, folder=folder)

    _create_raw_material_folder(parent=parent, date=date)

    sub = parent / "ext. Material"
    for folder in ext_m_subfolder:
        create_folder(parent=sub, folder=folder)


def _create_raw_material_folder(parent: Path, date: datetime):
    sub = parent / "Rohmaterial"
    raw_subfolder = _day_folder(date=date)  # Subfolder for 'Rohmaterial'
    for folder in raw_subfolder:
        create_folder(parent=sub, folder=folder)


def _day_folder(date: datetime) -> List[str]:
    """Creates a folder for every day with subfolders 'Bilder' and 'Videos'"""
    letter = 97  # char for 'a'
    day_folders = []
    for i in range(10):
        day_folders.append(
            f'{chr(letter + i)}-{date.strftime("%d.%m")}-{date.strftime("%A")}/Bilder'
        )
        day_folders.append(
            f'{chr(letter + i)}-{date.strftime("%d.%m")}-{date.strftime("%A")}/Videos'
        )
        date = date + timedelta(days=1)
    day_folders.append(f"{chr(letter + 11)}-Sonstiges/Bilder")
    day_folders.append(f"{chr(letter + 11)}-Sonstiges/Videos")
    return day_folders
