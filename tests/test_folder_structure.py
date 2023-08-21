import os.path
from PyQt5.QtCore import QDate

from foldersetup import folder_structure


def test_folder_creation():
    parent = "./testData"
    date = QDate(2023, 8, 1)

    folder_structure.create_folder_structure(parent, date)
    assert os.path.exists(os.path.join(parent, "Zeltlagerfilm 2023", "Rohmaterial", "b-02.08-Mittwoch", "Bilder"))
