from datetime import datetime
from pathlib import Path
from unittest import mock
from unittest.mock import patch, PropertyMock

import input_mocks
import src.main.gui_main
from assethandling.basemodels import FolderTabInput, RawTabInput, ExcelInput, ExcelOption
from src.main.gui_main import main
from src.main.gui_main import MainWindow
from src.excel.excelmethods import save_sheets_to_excel


# this is a sample how to test the gui without actually doing the core work like copying
@mock.patch("sys.exit")
@mock.patch("src.main.runner.runners.run_folder_setup")  # change this to a more core function e.g. copy_file

@mock.patch("src.main.gui_main.MainWindow.get_folder_input")
def test_main(mock_input, mock_fn, sys):
    # moc.return_value = "asdf"
    mock_fn.return_value = "Test"
    mock_input.return_value = FolderTabInput(
            folder=Path.cwd(),
            date=datetime.now()
        )
    main()
    assert type(mock_fn.call_args.kwargs["inputs"]) == FolderTabInput


@mock.patch("PyQt5.QtWidgets.QInputDialog.getText")
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_raw_input")
@mock.patch("pandas.DataFrame.to_excel")
def test_excel_creation_override(mock_fn, mock_input, sys, mock_input_dialog):
    mock_input_dialog.return_value = "j", True
    mock_fn.return_value = None
    mock_input.return_value = RawTabInput(
        do_structure=False,
        do_rename=False,
        fill_excel=False,
        create_picture_folder=False,
        raw_material_folder=input_mocks.TEST_PATH,
        first_folder_date=datetime.now(),
        excel=input_mocks.excel_input_manual,
        picture_folder=input_mocks.TEST_PATH
    )
    main()
    assert mock_fn.call_count == 2
    assert mock_fn.call_args_list[0][1]["sheet_name"] == "Videos"
    assert mock_fn.call_args_list[1][1]["sheet_name"] == "Bilder"


@mock.patch("PyQt5.QtWidgets.QInputDialog.getText")
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_raw_input")
@mock.patch("pandas.DataFrame.to_excel")
def test_excel_creation_no_override(mock_fn, mock_input, sys, mock_input_dialog):
    mock_input_dialog.return_value = "n", True
    mock_fn.return_value = None
    mock_input.return_value = RawTabInput(
        do_structure=False,
        do_rename=False,
        fill_excel=False,
        create_picture_folder=False,
        raw_material_folder=input_mocks.TEST_PATH,
        first_folder_date=datetime.now(),
        excel=input_mocks.excel_input_manual,
        picture_folder=input_mocks.TEST_PATH
    )
    main()
    assert mock_fn.call_count == 0
