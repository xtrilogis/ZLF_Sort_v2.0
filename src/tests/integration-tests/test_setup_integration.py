"""Just click the "Erstellen" button no inputs needed."""
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from assethandling.basemodels import FolderTabInput
from gui_main import main

TEST_PATH = Path.cwd().parent / "testData"

@patch("src.runner.runners.setup_methods.create_folder")
@patch("sys.exit")
@patch("gui_main.MainWindow.get_folder_input")
def test_folder_setup(mock_input, _, mock_fn, dummy_folder):
    mock_input.return_value = FolderTabInput(
        folder=dummy_folder, date=datetime(2023, 10, 5)
    )
    mock_fn.return_value = Path("test/path/")

    main()
    assert mock_fn.call_count == 31
    assert mock_fn.call_args_list[1].kwargs["parent"] == Path("test/path")


# test not a valid folder contains Rohmaterial, not a folder, not existing
# test if (either send_problems or) input error

@patch("src.runner.runners.setup_methods.create_folder")
@patch("sys.exit")
@patch("gui_main.MainWindow.get_folder_input")
def test_folder_setup_errors(mock_input, _, mock_fn, testdata_path, dummy_file):
    """Test if errors are handled appropriately
    three button pushes with three pop ups"""
    mock_input.side_effect = [
        FolderTabInput(folder="Not/existent/folder/", date=datetime(2023, 10, 5)),
        FolderTabInput(
            folder=testdata_path / "Rohmaterial/structured1", date=datetime(2023, 10, 5)
        ),
        FolderTabInput(folder=dummy_file, date=datetime(2023, 10, 5)),
    ]
    mock_fn.return_value = Path("test/path/")

    main()
    assert mock_fn.call_count == 0
