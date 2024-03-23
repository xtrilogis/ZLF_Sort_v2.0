from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from input_mocks import (TEST_DATE, TEST_PATH, excel_input_manual,
                         excel_input_standard)

from assethandling.basemodels import ExcelInput, ExcelOption, RawTabInput
from gui_main import main


@patch("src.main.runner.runners.raw_methods.copy_file")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_raw_input")
def test_run_correct_structure(mock_input, _, mock_fn):
    paths = ["raw/unstructured/Rohmaterial", "raw/structured1", "raw/structured2"]
    expectation = [28, 56, 84]  # eig aber check structure fehlt [28, 28, 56]
    for num, value in enumerate(paths):
        mock_input.return_value = RawTabInput(
            raw_material_folder=TEST_PATH / value,
            first_folder_date=datetime(2023, 7, 27),
            excel=excel_input_standard,
            picture_folder=TEST_PATH,
        )
        main()
        assert mock_fn.call_count == expectation[num]


@patch("src.main.runner.runners.raw_methods.copy_file")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_raw_input")
def test_run_correct_structure_errors(mock_input, _, mock_fn):
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH / "non existent",
        first_folder_date=datetime(2023, 7, 27),
        excel=excel_input_standard,
        picture_folder=TEST_PATH,
    )
    main()
    assert mock_fn.call_count == 0


@patch("pathlib.Path.rename")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_raw_input")
def test_run_rename(mock_input, _, mock_fn):
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH / "raw/structured1",
        first_folder_date=datetime(2023, 7, 27),
        excel=excel_input_standard,
        picture_folder=TEST_PATH,
    )
    main()
    assert mock_fn.call_count == 28
    assert Path(mock_fn.call_args_list[0].args[0]).name == "07_27_Do-001.jpg"


@patch("pathlib.Path.rename")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_raw_input")
def test_run_rename_errors(mock_input, _, mock_fn):
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH / "non existent",
        first_folder_date=datetime(2023, 7, 27),
        excel=excel_input_standard,
        picture_folder=TEST_PATH,
    )
    main()
    assert mock_fn.call_count == 0


@patch("PyQt5.QtWidgets.QInputDialog.getText")
@patch("excel.excelmethods.save_sheets_to_excel")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_raw_input")
def test_excel_creation_override(mock_input, _, mock_fn, mock_input_dialog):
    mock_input_dialog.return_value = "j", True
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH,
        first_folder_date=TEST_DATE,
        excel=excel_input_manual,
        picture_folder=TEST_PATH,
    )
    main()
    assert mock_fn.call_count == 2
    assert mock_fn.call_args_list[0][1]["sheet_name"] == "Videos"
    assert mock_fn.call_args_list[1][1]["sheet_name"] == "Bilder"


@patch("PyQt5.QtWidgets.QInputDialog.getText")
@patch("excel.excelmethods.save_sheets_to_excel")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_raw_input")
def test_excel_creation_no_override(mock_input, _, mock_fn, mock_input_dialog):
    mock_input_dialog.return_value = "n", True
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH,
        first_folder_date=datetime.now(),
        excel=excel_input_manual,
        picture_folder=TEST_PATH,
    )
    main()
    assert mock_fn.call_count == 0


@patch("src.main.runner.runners.raw_methods.save_sheets_to_excel")
@patch("src.main.runner.runners.raw_methods.create_emtpy_excel")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_raw_input")
def test_fill_excel_creation(mock_input, _, mock_create, mock_save):
    excel_input: ExcelInput = ExcelInput(
        option=ExcelOption.CREATE,
        name="ok_empty.xlsx",
        folder=TEST_PATH,
    )
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH,
        first_folder_date=TEST_DATE,
        excel=excel_input,
        picture_folder=TEST_PATH,
    )

    main()
    assert mock_create.call_count == 1
    assert mock_save.call_count == 1


@patch("PyQt5.QtWidgets.QInputDialog.getText")
@patch("src.main.runner.runners.raw_methods.save_sheets_to_excel")
@patch("excel.excelmethods.save_sheets_to_excel")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_raw_input")
def test_fill_excel_creation_override(
    mock_input, _, mock_fn1, mock_fn, mock_input_dialog
):
    mock_input_dialog.return_value = "j", True
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH,
        first_folder_date=TEST_DATE,
        excel=ExcelInput(
            option=ExcelOption.CREATE,
            name="ok_empty.xlsx",
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


@patch("src.main.runner.runners.raw_methods.save_sheets_to_excel")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_raw_input")
def test_fill_excel(mock_input, _, mock_fn):
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH,
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


@patch("src.main.runner.runners.raw_methods.save_sheets_to_excel")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_raw_input")
def test_fill_excel_errors(mock_input, _, mock_fn):
    mock_input.side_effect = [
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

    main()
    assert mock_fn.call_count == 0


@patch("pathlib.Path.mkdir")
@patch("src.main.runner.runners.raw_methods.copy_file")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_raw_input")
def test_run_create_picture_folder(mock_input, _, mock_fn, __):
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH / "raw/structured1",
        first_folder_date=datetime(2023, 7, 27),
        excel=excel_input_standard,
        picture_folder=TEST_PATH,
    )
    main()
    assert mock_fn.call_count == 18


@patch("pathlib.Path.mkdir")
@patch("src.main.runner.runners.raw_methods.copy_file")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_raw_input")
def test_run_create_picture_folder_errors(mock_input, _, mock_fn, __):
    mock_input.return_value = RawTabInput(
        raw_material_folder=TEST_PATH / "non existent",
        first_folder_date=datetime(2023, 7, 27),
        excel=excel_input_standard,
        picture_folder=TEST_PATH,
    )
    main()
    assert mock_fn.call_count == 0


@patch("src.main.runner.runners.raw_methods.create_emtpy_excel")
@patch("src.main.runner.runners.raw_methods.save_sheets_to_excel")
@patch("pathlib.Path.rename")
@patch("pathlib.Path.mkdir")
@patch("src.main.runner.runners.raw_methods.copy_file")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_raw_input")
def test_process_raw_full(
    mock_input, _, mock_copy, __, mock_rename, mock_save, mock_create
):
    mock_input.return_value = RawTabInput(
        do_structure=True,
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
    assert mock_copy.call_count == 28 + 18
    assert mock_rename.call_count == 28
    assert mock_save.call_count == 1
    assert mock_create.call_count == 0
