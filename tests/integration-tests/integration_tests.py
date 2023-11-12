from datetime import datetime
from pathlib import Path
from unittest import mock

import input_mocks
from assethandling.basemodels import FolderTabInput, RawTabInput, ExcelInput, ExcelOption
from src.main.gui_main import main

# this is a sample how to test the gui without actually doing the core work like copying
@mock.patch("src.main.runner.runners.run_folder_setup")  # change this to a more core function e.g. copy_file
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_folder_input")
def test_main(mock_input, sys, mock_fn):
    # moc.return_value = "asdf"
    mock_fn.return_value = "Test"
    mock_input.return_value = FolderTabInput(
            folder=input_mocks.TEST_PATH,
            date=datetime.now()
        )
    main()
    assert type(mock_fn.call_args.kwargs["inputs"]) == FolderTabInput

