from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import input_mocks
from assethandling.basemodels import FolderTabInput, RawTabInput, ExcelInput, ExcelOption
from src.main.gui_main import main

# this is a sample how to test the gui without actually doing the core work like copying
@patch("src.main.runner.runners.run_folder_setup")  # change this to a more core function e.g. copy_file
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_folder_input")
def test_main(mock_input, sys, mock_fn):
    mock_input.return_value = FolderTabInput(
            folder=input_mocks.TEST_PATH,
            date=datetime.now()
        )
    main()
    assert type(mock_fn.call_args.kwargs["inputs"]) == FolderTabInput

#  todo: one test per tab no input mock

# These test help checking the integration of ui inputs and the processing code
# Note that none of the button clicks result in a real creation or change in the given
# test data
@patch("src.main.runner.runners.setup_methods.create_folder")
@patch("sys.exit")
def test_folder_setup(_, mock_fn):
    mock_fn.return_value = Path("test/path/")
    main()
    assert mock_fn.call_count == 31
    assert mock_fn.call_args_list[1].kwargs['parent'] == Path("test/path")



@patch("excel.excelmethods.save_sheets_to_excel") # @patch("src.main.runner.runners.raw_methods.create_emtpy_excel") # erstetzen
@patch("src.main.runner.runners.raw_methods.save_sheets_to_excel")
@patch("pathlib.Path.rename")
@patch("pathlib.Path.mkdir")
@patch("src.main.runner.runners.raw_methods.copy_file")
@patch("sys.exit")
def test_process_raw_full(_, mock_copy, __, mock_rename, mock_save, mock_create):
    main()


@patch("pathlib.Path.mkdir")
@patch("src.main.runner.runners.util_methods.filemethods.copy_file")
@patch("sys.exit")
def test_run_process_util_full(_, mock_fn, __):
    main()
