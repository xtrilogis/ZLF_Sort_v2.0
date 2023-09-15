from unittest import mock
import pandas as pd
from rawmaterial.raw_material import correct_file_structure, run_rename, \
    fill_excel, create_picture_folder


@mock.patch("rawmaterial.raw_material.copy_file")
def test_correct_folder_structure(mock_copy, correct_raw):
    # TODO implementation
    pass


@mock.patch("rawmaterial.raw_material.rename_files")
def test_rename_files(mock_rename, correct_raw):
    run_rename(correct_raw)
    assert mock_rename.call_count == 4 # 31
    assert mock_rename.call_args_list[0].kwargs['folder'] == correct_raw / "a 27.07. Mi/Bilder"
    files = mock_rename.call_args_list[0].kwargs['all_files']
    assert files[0].date < files[-1].date


@mock.patch("pathlib.Path.glob")
@mock.patch("rawmaterial.raw_material.load_sheets_as_df")
@mock.patch("rawmaterial.raw_material.save_sheets_to_excel")
def test_fill_excel(mock_save, mock_load, mock_is_folder, testdata_path):
    mock_load.return_value = {
        "Videos": pd.DataFrame(columns=["Datei"]),
        "Bilder": pd.DataFrame(columns=["Datei"])
    }
    mock_is_folder.return_value = [testdata_path / "Zeltlagerfilm 2023"]
    fill_excel(excel=testdata_path, raw_material_folder=testdata_path / "Zeltlagerfilm 2023")
    assert mock_save.called
    assert len(mock_save.call_args.kwargs['sheets']) == 2
    assert len(mock_save.call_args.kwargs['sheets']['Videos']) == 3  # Ordner und 2 Videos
    assert len(mock_save.call_args.kwargs['sheets']['Bilder']) == 4


@mock.patch("rawmaterial.raw_material.copy_file")
def test_create_picture_folder(mock_copy, testdata_path):
    create_picture_folder(picture_folder=testdata_path,
                          raw_material_folder=testdata_path / "Zeltlagerfilm 2023")
    assert mock_copy.called
    assert mock_copy.call_count == 3
