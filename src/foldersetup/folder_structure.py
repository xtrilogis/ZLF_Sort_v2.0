import locale
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

locale.setlocale(locale.LC_TIME, 'de_DE.utf8')


def create_folder_structure(parent: Path, date: datetime):
    """Creates all necessary folders"""
    root_subfolder = ["Projekte", "Film", "Rohmaterial", "Schnittmaterial", "ext. Material"]
    raw_subfolder = day_folder(date=date)  # Subfolder for 'Rohmaterial'
    ext_m_subfolder = ["Dokumente", "Musik", "Grafiken"]  # Subfolder for 'ext. Material'

    parent = create_folder(parent, f'Zeltlagerfilm {date.year}')

    for folder in root_subfolder:
        create_folder(parent=parent, folder=folder)

    sub = parent / "Rohmaterial"
    for folder in raw_subfolder:
        create_folder(parent=sub, folder=folder)

    sub = parent / "ext. Material"
    for folder in ext_m_subfolder:
        create_folder(parent=sub, folder=folder)


def create_folder(parent: Path, folder: str) -> Path:
    create: Path = parent.joinpath(folder)
    if not create.exists():
        create.mkdir(parents=True)
    return create


def day_folder(date: datetime) -> List[str]:
    """Creates a folder for every day with subfolders 'Bilder' and 'Videos'"""
    letter = 97  # char for 'a'
    day_folders = []
    for i in range(10):
        day_folders.append(f'{chr(letter + i)}-{date.strftime("%d.%m")}-{date.strftime("%A")}/Bilder')
        day_folders.append(f'{chr(letter + i)}-{date.strftime("%d.%m")}-{date.strftime("%A")}/Videos')
        date = date + timedelta(days=1)
    day_folders.append(f'{chr(letter + 11)}-Sonstiges/Bilder')
    day_folders.append(f'{chr(letter + 11)}-Sonstiges/Videos')
    return day_folders
