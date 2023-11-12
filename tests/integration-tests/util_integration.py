from datetime import datetime
from pathlib import Path
from unittest import mock

from input_mocks import TEST_PATH
from assethandling.basemodels import UtilTabInput
from src.main.gui_main import main

# this is a sample how to test the gui without actually doing the core work like copying
@mock.patch("src.main.runner.runners.run_folder_setup")  # change this to a more core function e.g. copy_file
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_copy_sections(mock_input, _, mock_fn):
    # moc.return_value = "asdf"
    mock_fn.return_value = "Test"
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH,
        excel_full_filepath=TEST_PATH,
        do_sections= False,
        do_video_sections= False,
        do_picture_sections= False,
        rating_section=0,
        do_selections=False,
        videos_columns_selection=[],
        picture_columns_selection=[],
        marker="",
        do_search= False,
        videos_columns_search=[],
        picture_columns_search=[],
        keywords="",
        rating_search=0,
        create_picture_folder= False,
        rating_pictures=0
        )
    main()


@mock.patch("src.main.runner.runners.run_folder_setup")  # change this to a more core function e.g. copy_file
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_copy_sections_errors(mock_input, _, mock_fn):
    mock_fn.return_value = "Test"
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH,
        excel_full_filepath=TEST_PATH,
        )
    main()


@mock.patch("src.main.runner.runners.run_folder_setup")  # change this to a more core function e.g. copy_file
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_copy_selection(mock_input, _, mock_fn):
    mock_fn.return_value = "Test"
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH,
        excel_full_filepath=TEST_PATH,
        )
    main()


@mock.patch("src.main.runner.runners.run_folder_setup")  # change this to a more core function e.g. copy_file
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_copy_selection_errors(mock_input, _, mock_fn):
    mock_fn.return_value = "Test"
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH,
        excel_full_filepath=TEST_PATH,
        )
    main()


@mock.patch("src.main.runner.runners.run_folder_setup")  # change this to a more core function e.g. copy_file
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_search(mock_input, _, mock_fn):
    mock_fn.return_value = "Test"
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH,
        excel_full_filepath=TEST_PATH,
        )
    main()


@mock.patch("src.main.runner.runners.run_folder_setup")  # change this to a more core function e.g. copy_file
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_search_errors(mock_input, _, mock_fn):
    mock_fn.return_value = "Test"
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH,
        excel_full_filepath=TEST_PATH,
        )
    main()


@mock.patch("src.main.runner.runners.run_folder_setup")  # change this to a more core function e.g. copy_file
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_create_rated_picture_folder(mock_input, _, mock_fn):
    mock_fn.return_value = "Test"
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH,
        excel_full_filepath=TEST_PATH,
        )
    main()

@mock.patch("src.main.runner.runners.run_folder_setup")  # change this to a more core function e.g. copy_file
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_create_rated_picture_folder_errors(mock_input, _, mock_fn):
    mock_fn.return_value = "Test"
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH,
        excel_full_filepath=TEST_PATH,
        )
    main()


@mock.patch("src.main.runner.runners.run_folder_setup")  # change this to a more core function e.g. copy_file
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_statistics(mock_input, _, mock_fn):
    mock_fn.return_value = "Test"
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH,
        excel_full_filepath=TEST_PATH,
        )
    main()


@mock.patch("src.main.runner.runners.run_folder_setup")  # change this to a more core function e.g. copy_file
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_statistics_errors(mock_input, _, mock_fn):
    mock_fn.return_value = "Test"
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH,
        excel_full_filepath=TEST_PATH,
        )
    main()


@mock.patch("src.main.runner.runners.run_folder_setup")  # change this to a more core function e.g. copy_file
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_process_util_full(mock_input, _, mock_fn):
    mock_fn.return_value = "Test"
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH,
        excel_full_filepath=TEST_PATH,
        )
    main()


@mock.patch("src.main.runner.runners.run_folder_setup")  # change this to a more core function e.g. copy_file
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_process_util_full_errors(mock_input, _, mock_fn):
    mock_fn.return_value = "Test"
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH,
        excel_full_filepath=TEST_PATH,
        )
    main()