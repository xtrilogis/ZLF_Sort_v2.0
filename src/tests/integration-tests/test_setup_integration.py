from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from assethandling.basemodels import FolderTabInput
from gui_main import main


@patch("src.runner.runners.setup_methods.create_folder")
@patch("sys.exit")
@patch("src.gui_main.MainWindow.get_folder_input")
def test_folder_setup(mock_input, _, mock_fn):
    mock_input.return_value = FolderTabInput(
        folder=Path.cwd(), date=datetime(2023, 10, 5)
    )
    mock_fn.return_value = Path("test/path/")

    main()
    assert mock_fn.call_count == 31


# test not a valid folder contains Rohmaterial, not a folder, not existing
# test if (either send_problems or) input error

TEST_PATH = Path.cwd() / "testData"


@patch("src.runner.runners.setup_methods.create_folder")
@patch("sys.exit")
@patch("src.gui_MainWindow.get_folder_input")
def test_folder_setup_errors(mock_input, sys, mock_fn):
    mock_input.side_effect = [
        FolderTabInput(folder="Path.cwd()", date=datetime(2023, 10, 5)),
        FolderTabInput(
            folder=TEST_PATH / "Rohmaterial/structured1", date=datetime(2023, 10, 5)
        ),
    ]
    mock_fn.return_value = Path("test/path/")

    main()
    assert mock_fn.call_count == 0
