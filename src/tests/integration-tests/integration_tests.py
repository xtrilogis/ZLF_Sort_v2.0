from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import input_mocks

from assethandling.basemodels import (
    ExcelInput,
    ExcelOption,
    FolderTabInput,
    RawTabInput,
)
from gui_main import main

# SAMPLE
# this is a sample how to test the gui without actually doing the core work like copying
# change The first patch to a more core function e.g. copy_file
# if necessary add further patches
@patch("runner.runners.run_folder_setup")
@patch("sys.exit")
@patch("gui_main.MainWindow.get_folder_input")
def test_main(mock_input, sys, mock_fn):
    mock_input.return_value = FolderTabInput(
        folder=input_mocks.TEST_PATH, date=datetime.now()
    )
    main()
    assert type(mock_fn.call_args.kwargs["inputs"]) == FolderTabInput


# INTEGRATION TESTS
# These test help checking the integration of ui inputs and the processing code
# Though you need to fill in the inputs, button clicks shouldn't
# result in a real creation or change in the given test data
# This test is for clicking around the app for manual testing


@patch("excel.excelmethods.save_sheets_to_excel")
# @patch("runner.runners.raw_methods.create_emtpy_excel") # ersetzen
@patch("runner.runners.raw_methods.save_sheets_to_excel")
@patch("pathlib.Path.rename")
@patch("pathlib.Path.mkdir")
@patch("runner.runners.raw_methods.copy_file")
@patch("sys.exit")
def test_process_raw_full(_, mock_copy, __, mock_rename, mock_save, mock_create):
    main()


@patch("pathlib.Path.mkdir")
@patch("runner.runners.util_methods.filemethods.copy_file")
@patch("sys.exit")
def test_run_process_util_full(_, mock_fn, __):
    main()
