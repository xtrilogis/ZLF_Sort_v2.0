import os.path
from datetime import datetime
from pathlib import Path
from unittest import mock

from PyQt5.QtCore import QDate

import src.foldersetup.folder_structure
from foldersetup import folder_structure

ROOT = Path.cwd() / "testData"


@mock.patch("foldersetup.folder_structure.create_folder")
def test_folder_creation(mock_create_folder):
    mock_create_folder.return_value = Path(".")
    date = datetime.now()

    folder_structure.create_folder_structure(ROOT, date)
    assert mock_create_folder.called
    assert mock_create_folder.call_count == 31  # wegen 31 Ordnern
