from datetime import datetime
from unittest import mock

from foldersetup.folder_setup import create_folder_structure


@mock.patch("foldersetup.folder_setup.create_folder")
def test_folder_creation(mock_create_folder, testdata_path):
    date = datetime.now()
    mock_create_folder.return_value = testdata_path / f'Zeltlagerfilm {date.year}'

    create_folder_structure(testdata_path, date)
    assert mock_create_folder.called
    assert mock_create_folder.call_count == 31  # wegen 31 Ordnern
    assert mock_create_folder.call_args_list[0].kwargs['parent'] == testdata_path
    assert mock_create_folder.call_args_list[0].kwargs['folder'] == f'Zeltlagerfilm {date.year}'
