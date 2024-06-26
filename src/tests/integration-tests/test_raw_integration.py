import shutil
from datetime import datetime
from pathlib import Path
from typing import List
from unittest.mock import patch

from input_mocks import TEST_DATE, TEST_PATH, excel_input_manual, excel_input_standard

from assethandling.basemodels import ExcelInput, ExcelOption, RawTabInput
from gui_main import main


@patch("runner.runners.raw_methods.copy_file")
@patch("sys.exit")
@patch("gui_main.MainWindow.get_raw_input")
def test_run_correct_structure(mock_input, _, mock_fn):
    """How to use: this test will start the UI for every test path
    - push "Richtige Struktur"
    - wait till its finished
    - close the window"""
    paths = ["raw/unstructured/Rohmaterial", "raw/structured1", "raw/structured2"]
    expectation = [29, 58, 87]
    for index, value in enumerate(paths):
        mock_input.return_value = RawTabInput(
            raw_material_folder=TEST_PATH / value,
            first_folder_date=datetime(2023, 7, 27),
            excel=excel_input_standard,
            picture_folder=TEST_PATH,
        )
        main()
        assert mock_fn.call_count == expectation[index]
        shutil.rmtree((TEST_PATH / value).parent / "New")


@patch("PyQt5.QtWidgets.QInputDialog.getItem")
@patch("runner.runners.raw_methods.copy_file")
@patch("sys.exit")
@patch("gui_main.MainWindow.get_raw_input")
def test_run_correct_structure_errors(mock_input, _, mock_fn, mock_dialog):
    """How to use: this test will start the UI for every test path
        - push "Richtige Struktur"
        - wait for the error message and close it
        - wait till the process is finished
        - close the window"""
    mock_dialog.return_value = "Nein", True
    paths = ["Non existent", "dummy/Rohmaterial"]
    for index, value in enumerate(paths):
        mock_input.return_value = RawTabInput(
            raw_material_folder=TEST_PATH / value,
            first_folder_date=datetime(2023, 7, 27),
            excel=excel_input_standard,
            picture_folder=TEST_PATH,
        )
        main()
        assert mock_fn.call_count == 0


@patch("pathlib.Path.rename")
@patch("sys.exit")
@patch("gui_main.MainWindow.get_raw_input")
def test_run_rename(mock_input, _, mock_fn):
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH / "raw/structured1",
        first_folder_date=datetime(2023, 7, 27),
        excel=excel_input_standard,
        picture_folder=TEST_PATH,
    )
    main()
    assert mock_fn.call_count == 29
    assert Path(mock_fn.call_args_list[0].args[0]).name == "07_27_Do-001.jpg"


@patch("pathlib.Path.rename")
@patch("sys.exit")
@patch("gui_main.MainWindow.get_raw_input")
def test_run_rename_errors(mock_input, _, mock_fn):
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH / "non existent",
        first_folder_date=datetime(2023, 7, 27),
        excel=excel_input_standard,
        picture_folder=TEST_PATH,
    )
    main()
    assert mock_fn.call_count == 0


@patch("PyQt5.QtWidgets.QInputDialog.getItem")
@patch("excel.excelmethods.save_sheets_to_excel")
@patch("sys.exit")
@patch("gui_main.MainWindow.get_raw_input")
def test_excel_creation_override(mock_input, _, mock_fn, mock_dialog):
    mock_dialog.return_value = "Ja", True
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH,
        first_folder_date=TEST_DATE,
        excel=excel_input_manual,
        picture_folder=TEST_PATH,
    )
    main()
    assert mock_fn.call_count == 1
    assert mock_fn.call_args_list[0][1]['path'] == Path(TEST_PATH) / "Zeltlagerfilm custom.xlsx"
    assert "Videos" in mock_fn.call_args_list[0][1]['sheets'].keys()
    assert "Bilder" in mock_fn.call_args_list[0][1]['sheets'].keys()
    assert excel_input_manual.picture_columns[0] in mock_fn.call_args_list[0][1]['sheets']["Bilder"].columns


@patch("PyQt5.QtWidgets.QInputDialog.getItem")
@patch("excel.excelmethods.save_sheets_to_excel")
@patch("sys.exit")
@patch("gui_main.MainWindow.get_raw_input")
def test_excel_creation_no_override(mock_input, _, mock_fn, mock_input_dialog):
    mock_input_dialog.return_value = "Nein", True
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH,
        first_folder_date=datetime.now(),
        excel=excel_input_manual,
        picture_folder=TEST_PATH,
    )
    main()
    assert mock_fn.call_count == 0


@patch("runner.runners.raw_methods.save_sheets_to_excel")
@patch("runner.runners.raw_methods.create_emtpy_excel")
@patch("sys.exit")
@patch("gui_main.MainWindow.get_raw_input")
def test_fill_excel_creation(mock_input, _, mock_create, mock_save):
    excel_input: ExcelInput = ExcelInput(
        option=ExcelOption.CREATE,
        name="ok_empty.xlsx",
        folder=TEST_PATH,
    )
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH / "raw/structured1",
        first_folder_date=TEST_DATE,
        excel=excel_input,
        picture_folder=TEST_PATH,
    )

    main()
    assert mock_create.call_count == 1
    assert mock_save.call_count == 1


@patch("PyQt5.QtWidgets.QInputDialog.getItem")
@patch("runner.runners.raw_methods.save_sheets_to_excel")
@patch("excel.excelmethods.save_sheets_to_excel")
@patch("sys.exit")
@patch("gui_main.MainWindow.get_raw_input")
def test_fill_excel_creation_override(
    mock_input, _, mock_fn1, mock_fn, mock_input_dialog
):
    mock_input_dialog.return_value = "Ja", True
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH / "raw/structured1",
        first_folder_date=TEST_DATE,
        excel=ExcelInput(
            option=ExcelOption.CREATE,
            name="Zeltlagerfilm custom.xlsx",
            folder=TEST_PATH,
        ),
        picture_folder=TEST_PATH,
    )
    main()
    assert mock_input_dialog.call_count == 1
    assert mock_fn.call_count == 1
    assert mock_fn1.call_count == 1
    assert "Videos" in mock_fn.call_args_list[0].kwargs["sheets"].keys()
    assert "Bilder" in mock_fn.call_args_list[0].kwargs["sheets"].keys()


@patch("runner.runners.raw_methods.save_sheets_to_excel")
@patch("sys.exit")
@patch("gui_main.MainWindow.get_raw_input")
def test_fill_excel(mock_input, _, mock_fn):
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH / "raw/structured1",
        first_folder_date=TEST_DATE,
        excel=ExcelInput(
            option=ExcelOption.EXISTING,
            name="ok_empty.xlsx",
            folder=TEST_PATH,
        ),
        picture_folder=TEST_PATH,
    )
    main()
    assert mock_fn.call_count == 1
    assert mock_fn.call_args_list[0][1]["path"] == TEST_PATH / "ok_empty.xlsx"
    assert mock_fn.call_args_list[0][1]["sheets"]["Videos"].shape[0] == 13


@patch("runner.runners.raw_methods.save_sheets_to_excel")
@patch("sys.exit")
@patch("gui_main.MainWindow.get_raw_input")
def test_fill_excel_errors(mock_input, _, mock_fn):
    # How to use: click the button for every side effect
    mocks: List[RawTabInput] = [
        RawTabInput(
            raw_material_folder=TEST_PATH,
            first_folder_date=TEST_DATE,
            excel=ExcelInput(
                option=ExcelOption.EXISTING,
                name="ok_data.xlsx",
                folder=TEST_PATH,
            ),
            picture_folder=TEST_PATH,
        ),
        RawTabInput(
            raw_material_folder=TEST_PATH,
            first_folder_date=TEST_DATE,
            excel=ExcelInput(
                option=ExcelOption.EXISTING,
                name="missing_columns.xlsx",
                folder=TEST_PATH,
            ),
            picture_folder=TEST_PATH,
        ),
        RawTabInput(
            raw_material_folder=TEST_PATH,
            first_folder_date=TEST_DATE,
            excel=ExcelInput(
                option=ExcelOption.EXISTING,
                name="missing_sheet.xlsx",
                folder=TEST_PATH,
            ),
            picture_folder=TEST_PATH,
        ),
    ]
    for mock in mocks:
        mock_input.return_value = mock
        main()
        assert mock_fn.call_count == 0


@patch("pathlib.Path.mkdir")
@patch("runner.runners.raw_methods.copy_file")
@patch("sys.exit")
@patch("gui_main.MainWindow.get_raw_input")
def test_run_create_picture_folder(mock_input, _, mock_fn, __):
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH / "raw/structured1",
        first_folder_date=datetime(2023, 7, 27),
        excel=excel_input_standard,
        picture_folder=TEST_PATH,
    )
    main()
    assert mock_fn.call_count == 19


@patch("pathlib.Path.mkdir")
@patch("runner.runners.raw_methods.copy_file")
@patch("sys.exit")
@patch("gui_main.MainWindow.get_raw_input")
def test_run_create_picture_folder_errors(mock_input, _, mock_fn, __):
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH / "non existent",
        first_folder_date=datetime(2023, 7, 27),
        excel=excel_input_standard,
        picture_folder=TEST_PATH,
    )
    mocks = [
        RawTabInput(
            raw_material_folder=TEST_PATH / "non existent",
            first_folder_date=datetime(2023, 7, 27),
            excel=excel_input_standard,
            picture_folder=TEST_PATH,
        ),
        RawTabInput(
            raw_material_folder=TEST_PATH / "raw/structured1",
            first_folder_date=datetime(2023, 7, 27),
            excel=excel_input_standard,
            picture_folder=TEST_PATH / "non existent",
        )
    ]
    for mock in mocks:
        mock_input.return_value = mock
        main()
        assert mock_fn.call_count == 0


@patch("runner.runners.raw_methods.create_emtpy_excel")
@patch("runner.runners.raw_methods.save_sheets_to_excel")
@patch("pathlib.Path.rename")
@patch("pathlib.Path.mkdir")
@patch("runner.runners.raw_methods.copy_file")
@patch("sys.exit")
@patch("gui_main.MainWindow.get_raw_input")
def test_process_raw_full(
    mock_input, _, mock_copy, __, mock_rename, mock_save, mock_create
):
    mock_input.return_value = RawTabInput(
        do_rename=True,
        fill_excel=True,
        create_picture_folder=True,
        raw_material_folder=TEST_PATH / "raw/structured2",
        first_folder_date=datetime(2023, 7, 27),
        excel=ExcelInput(
            option=ExcelOption.EXISTING,
            name="ok_empty.xlsx",
            folder=TEST_PATH,
        ),
        picture_folder=TEST_PATH,
    )
    main()
    assert mock_copy.call_count == 19
    assert mock_rename.call_count == 29
    assert mock_save.call_count == 1
    assert mock_create.call_count == 0
