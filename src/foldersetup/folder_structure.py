import os
from PyQt5.QtCore import QDate


def create_folder_structure(parent: str, date: QDate):
    """Creates all necessary folders"""
    root_subfolder = ["Projekte", "Film", "Rohmaterial", "Schnittmaterial", "ext. Material"]
    raw_subfolder = day_folder(date=date)  # Subfolder for 'Rohmaterial'
    ext_m_subfolder = ["Dokumente", "Musik", "Grafiken"]  # Subfolder for 'ext. Material'

    parent = os.path.join(parent, f'Zeltlagerfilm {date.year()}')
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
    letter = 97  # char for 'a'
    day_folders = []
    for i in range(10):
        day_folders.append(f'{chr(letter + i)}-{date.toString("dd.MM")}-{date.toString("dddd")}/Bilder')
        day_folders.append(f'{chr(letter + i)}-{date.toString("dd.MM")}-{date.toString("dddd")}/Videos')
        date = date.addDays(1)
    day_folders.append(f'{chr(letter + 11)}-Sonstiges/Bilder')
    day_folders.append(f'{chr(letter + 11)}-Sonstiges/Videos')
    return day_folders
