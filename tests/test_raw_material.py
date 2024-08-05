from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

import pandas as pd

from assethandling.basemodels import ExcelConfig, SheetConfig
from rawmaterial.raw_material import (
    # correct_file_structure,
    create_excel,
    create_picture_folder,
    fill_excel,
    run_rename,
)


@mock.patch("rawmaterial.raw_material.rename_files")
def test_rename_files(mock_rename, correct_raw):
    mock_callback = MagicMock()
    run_rename(correct_raw, mock_callback)
    assert mock_rename.call_count == 6  # Number of folders with files to rename
    assert (
        mock_rename.call_args_list[0].kwargs["folder"]
        == correct_raw / "a 27.07.-Do/Bilder"
    )
    files = mock_rename.call_args_list[0].kwargs["all_files"]
    assert files[0].date < files[-1].date


@mock.patch("rawmaterial.raw_material.create_emtpy_excel")
def test_create_excel(mock_create, testdata_path):
    mock_callback = MagicMock()
    mock_get_data = MagicMock(return_value="Nein")
    s = SheetConfig(name="sdfs", columns=["a", "b", "c", "d"])
    config = ExcelConfig(excel_folder=testdata_path / "raw", sheets=[s])
    create_excel(config=config, progress_callback=mock_callback, get_data=mock_get_data)
    assert mock_create.call_count == 1


@mock.patch("excel.excelmethods.save_sheets_to_excel")
def test_create_excel_bad(mock_create, testdata_path):
    mock_callback = MagicMock()
    mock_get_data = MagicMock(return_value="Nein")
    config = ExcelConfig(
        excel_folder=testdata_path,
        excel_file_name="ok_empty.xlsx",
        sheets=[SheetConfig(name="name", columns=["Datei"])],
    )
    create_excel(config=config, progress_callback=mock_callback, get_data=mock_get_data)
    assert mock_create.call_count == 0


@mock.patch("pathlib.Path.glob")
@mock.patch("rawmaterial.raw_material.load_sheets_as_df")
@mock.patch("rawmaterial.raw_material.save_sheets_to_excel")
def test_fill_excel(mock_save, mock_load, mock_is_folder, correct_raw):
    mock_callback = MagicMock()
    mock_load.return_value = {
        "Videos": pd.DataFrame(columns=["Datei"]),
        "Bilder": pd.DataFrame(columns=["Datei"]),
    }
    mock_is_folder.return_value = [correct_raw / "a 27.07.-Do/Bilder"]
    fill_excel(
        excel=Path(""), raw_material_folder=correct_raw, progress_callback=mock_callback
    )
    assert mock_save.called
    assert len(mock_save.call_args.kwargs["sheets"]) == 2
    assert len(mock_save.call_args.kwargs["sheets"]["Videos"]) == 0
    assert len(mock_save.call_args.kwargs["sheets"]["Bilder"]) == 7  # header + 6 files


@mock.patch("rawmaterial.raw_material.copy_file")
def test_create_picture_folder(mock_copy, correct_raw):
    mock_callback = MagicMock()
    create_picture_folder(
        picture_folder=correct_raw.parent,
        raw_material_folder=correct_raw,
        progress_callback=mock_callback,
    )
    assert mock_copy.called
    assert mock_copy.call_count == 19
