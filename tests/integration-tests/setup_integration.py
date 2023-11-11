from datetime import datetime
from pathlib import Path
from unittest import mock

from assethandling.basemodels import FolderTabInput
from src.main.gui_main import main


@mock.patch("src.main.runner.runners.run_folder_setup")
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_folder_input")
def test_folder_setup(mock_input, sys, mock_fn):
    mock_input.return_value = FolderTabInput(
            folder=Path.cwd(),
            date=datetime(2023, 10, 5)
        )
    mock_fn.return_value = "Test"
    main()
    assert type(mock_fn.call_args.kwargs["inputs"]) == FolderTabInput
    # mock Path.mkdir / filemethods.create_folder
    # assert called the right amount of times

# test not a valid folder contains Rohmaterial, not a folder, not existing
# test if (either send_problems or) input error
