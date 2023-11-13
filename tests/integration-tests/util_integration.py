from datetime import datetime
from pathlib import Path
from unittest import mock

from input_mocks import TEST_PATH
from assethandling.basemodels import UtilTabInput
from src.main.gui_main import main

# this is a sample how to test the gui without actually doing the core work like copying
@mock.patch("pathlib.Path.mkdir")
@mock.patch("src.main.runner.runners.util_methods.filemethods.copy_file")  # change this to a more core function e.g. copy_file
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_copy_sections(mock_input, _, mock_fn, __):
    # moc.return_value = "asdf"
    mock_fn.return_value = "Test"
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH,
        excel_full_filepath=TEST_PATH / "util/Zeltlagerfilm 2023.xlsx",
        do_sections=True,
        do_video_sections=True,
        do_picture_sections=True,
        rating_section=4,
    )
    main()
    assert  mock_fn.call_count == 17 # first call dest folder contains Schnittmaterial, parent == raw.parent
    # assert  mock_fn.call_count == 7 # nur Videos
    assert mock_fn.call_args_list[0].kwargs["src_file"].name == "07_27_Do-002.MP4"
    # assert mock_fn.call_count == 10 # nur Bilder
    # assert mock_fn.call_args_list[0].kwargs["src_file"].name == "07_27_Do-001.jpg"
    assert "Schnittmaterial" in mock_fn.call_args_list[0].kwargs["dst_folder"].parts




@mock.patch("src.main.runner.runners.util_methods.filemethods.copy_file")  # change this to a more core function e.g. copy_file
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_copy_sections_errors(mock_input, _, mock_fn):
    # empty sheet
    mock_fn.return_value = "Test"
    mock_input.side_effect = [
        UtilTabInput(
            raw_material_folder=TEST_PATH,
            excel_full_filepath=TEST_PATH / "ok_empty.xlsx",
            do_sections=True,
            do_video_sections=True,
            do_picture_sections=True,
            rating_section=4,
        ),
        UtilTabInput(
            raw_material_folder=TEST_PATH,
            excel_full_filepath=TEST_PATH / "ok_data.xlsx",
            do_sections=True,
            do_video_sections=True,
            do_picture_sections=True,
            rating_section=8,
        ),
        UtilTabInput(
            raw_material_folder=TEST_PATH,
            excel_full_filepath=TEST_PATH / "duplicated_data.xlsx",
            do_sections=True,
            do_video_sections=True,
            do_picture_sections=True,
            rating_section=4,
        )
    ]
    main()
    assert mock_fn.call_count == 0



@mock.patch("src.main.runner.runners.run_folder_setup")  # change this to a more core function e.g. copy_file
@mock.patch("sys.exit")
@mock.patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_copy_selection(mock_input, _, mock_fn):
    mock_fn.return_value = "Test"
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH,
        excel_full_filepath=TEST_PATH,
        # rating 4
        )
    main()
    # NZS b5 Outtakes b5, Video Outtakes 4


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
    # Videos Name: Bilder Test: 6 (4) Name: 4 (2) bw 4


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
    # 10

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