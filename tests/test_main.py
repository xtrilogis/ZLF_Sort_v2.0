from datetime import datetime
from pathlib import Path
from unittest import mock
from unittest.mock import patch, PropertyMock
from assethandling.basemodels import FolderTabInput
from src.main.gui_main import main
from src.main.gui_main import MainWindow


# this is a sample how to test the gui without actually doing the core work like copying
@mock.patch("sys.exit")
@mock.patch("src.main.adapt.runners.run_folder_setup")  # change this to a more core function e.g. copy_file
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
