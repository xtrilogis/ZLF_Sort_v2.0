from unittest.mock import patch

from input_mocks import TEST_PATH

from assethandling.basemodels import UtilTabInput
from gui_main import main


# this is a sample how to test the gui without actually doing the core work like copying
@patch("src.main.gui_main.MainWindow.util_buttons_status")
@patch("pathlib.Path.mkdir")
@patch("src.main.runner.runners.util_methods.filemethods.copy_file")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_copy_sections(mock_input, _, mock_fn, __, ___):
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH / "util/Rohmaterial",
        excel_full_filepath=TEST_PATH / "util/Zeltlagerfilm 2023.xlsx",
        do_sections=True,
        do_video_sections=True,
        do_picture_sections=True,
        rating_section=4,
    )
    main()
    assert (
        mock_fn.call_count == 17
    )  # first call dest folder contains Schnittmaterial, parent == raw.parent
    # assert  mock_fn.call_count == 7 # nur Videos
    assert mock_fn.call_args_list[0].kwargs["src_file"].name == "07_27_Do-002.MP4"
    # assert mock_fn.call_count == 10 # nur Bilder
    # assert mock_fn.call_args_list[0].kwargs["src_file"].name == "07_27_Do-001.jpg"
    assert "Schnittmaterial" in mock_fn.call_args_list[0].kwargs["dst_folder"].parts


@patch("src.main.gui_main.MainWindow.util_buttons_status")
@patch("src.main.runner.runners.util_methods.filemethods.copy_file")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_copy_sections_errors(mock_input, _, mock_fn, __):
    mock_input.side_effect = [
        UtilTabInput(
            raw_material_folder=TEST_PATH / "util/Rohmaterial",
            excel_full_filepath=TEST_PATH / "ok_empty.xlsx",
            do_sections=True,
            do_video_sections=True,
            do_picture_sections=True,
            rating_section=4,
        ),
        UtilTabInput(
            raw_material_folder=TEST_PATH / "util/Rohmaterial",
            excel_full_filepath=TEST_PATH / "util/Zeltlagerfilm 2023.xlsx",
            do_sections=True,
            do_video_sections=True,
            do_picture_sections=True,
            rating_section=8,
        ),
        UtilTabInput(
            raw_material_folder=TEST_PATH / "util/Rohmaterial",
            excel_full_filepath=TEST_PATH / "duplicated_data.xlsx",
            do_sections=True,
            do_video_sections=True,
            do_picture_sections=True,
            rating_section=4,
        ),
    ]
    main()
    assert mock_fn.call_count == 0


@patch("src.main.gui_main.MainWindow.util_buttons_status")
@patch("src.main.runner.runners.util_methods.filemethods.copy_file")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_copy_selection(mock_input, _, mock_fn, __):
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH / "util/Rohmaterial",
        excel_full_filepath=TEST_PATH / "util/Zeltlagerfilm 2023.xlsx",
        do_selections=True,
        videos_columns_selection=["Outtakes (x)"],  # 4 Files
        picture_columns_selection=["NZS (x)", "Outtakes (x)"],  # 5 and 4
        marker="x",
    )
    main()
    assert mock_fn.call_count == 13


@patch("src.main.gui_main.MainWindow.util_buttons_status")
@patch("src.main.runner.runners.util_methods.filemethods.copy_file")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_copy_selection_errors(mock_input, _, mock_fn, __):
    mock_input.side_effect = [
        UtilTabInput(
            raw_material_folder=TEST_PATH / "util/Rohmaterial",
            excel_full_filepath=TEST_PATH / "ok_empty.xlsx",
            do_selections=True,
            videos_columns_selection=["Outtakes"],
            picture_columns_selection=["NZS", "Outtakes"],
            marker="x",
        ),
        UtilTabInput(
            raw_material_folder=TEST_PATH / "util/Rohmaterial",
            excel_full_filepath=TEST_PATH / "util/Zeltlagerfilm 2023.xlsx",
            do_selections=True,
            videos_columns_selection=["Outtakes"],
            picture_columns_selection=["Outtakes"],
            marker="marker",
        ),
        UtilTabInput(
            raw_material_folder=TEST_PATH / "util/Rohmaterial",
            excel_full_filepath=TEST_PATH / "util/Zeltlagerfilm 2023.xlsx",
            do_selections=True,
            videos_columns_selection=["not existing (x)"],
            picture_columns_selection=[""],
            marker="marker",
        ),
        UtilTabInput(
            raw_material_folder=TEST_PATH / "util/Rohmaterial",
            excel_full_filepath=TEST_PATH / "duplicated_data.xlsx",
            do_selections=True,
            videos_columns_selection=["Outtakes (x)"],
            picture_columns_selection=["NZS (x)", "Outtakes (x)"],
            marker="x",
        ),
    ]
    main()
    assert mock_fn.call_count == 0


@patch("src.main.gui_main.MainWindow.util_buttons_status")
@patch("src.main.runner.runners.util_methods.filemethods.copy_file")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_search(mock_input, _, mock_fn, __):
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH / "util/Rohmaterial",
        excel_full_filepath=TEST_PATH / "util/Zeltlagerfilm 2023.xlsx",
        do_search=True,
        videos_columns_search=["Bemerkung"],  # 4 (2)
        picture_columns_search=["Bemerkung"],  # 4 (2), 6 (4)
        keywords=["name", "Name", "Test"],
        rating_search=4,
    )
    main()
    assert mock_fn.call_count == 8


@patch("src.main.gui_main.MainWindow.util_buttons_status")
@patch("src.main.runner.runners.util_methods.filemethods.copy_file")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_search_errors(mock_input, _, mock_fn, __):
    mock_input.side_effect = [
        UtilTabInput(
            raw_material_folder=TEST_PATH / "util/Rohmaterial",
            excel_full_filepath=TEST_PATH / "ok_empty.xlsx",
            do_search=True,
            videos_columns_search=["Bemerkung"],  # 4 (2)
            picture_columns_search=["Bemerkung"],  # 4 (2), 6 (4)
            keywords=["name", "Name", "Test"],
            rating_search=4,
        ),
        UtilTabInput(
            raw_material_folder=TEST_PATH / "util/Rohmaterial",
            excel_full_filepath=TEST_PATH / "util/Zeltlagerfilm 2023.xlsx",
            do_search=True,
            videos_columns_search=["Bemerkung"],  # 4 (2)
            picture_columns_search=["Bemerkung"],  # 4 (2), 6 (4)
            keywords=["name", "Name", "Test"],
            rating_search=8,
        ),
        UtilTabInput(
            raw_material_folder=TEST_PATH / "util/Rohmaterial",
            excel_full_filepath=TEST_PATH / "util/Zeltlagerfilm 2023.xlsx",
            do_search=True,
            videos_columns_search=["Not-existing"],  # 4 (2)
            picture_columns_search=["Bemerkung"],  # 4 (2), 6 (4)
            keywords=["name", "Name", "Test"],
            rating_search=4,
        ),
        UtilTabInput(
            raw_material_folder=TEST_PATH / "util/Rohmaterial",
            excel_full_filepath=TEST_PATH / "duplicated_data.xlsx",
            do_search=True,
            videos_columns_search=["Bemerkung"],  # 4 (2)
            picture_columns_search=["Bemerkung"],  # 4 (2), 6 (4)
            keywords=["name", "Name", "Test"],
            rating_search=4,
        ),
    ]
    main()
    assert mock_fn.call_count == 0


@patch("src.main.gui_main.MainWindow.util_buttons_status")
@patch("src.main.runner.runners.util_methods.filemethods.copy_file")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_create_rated_picture_folder(mock_input, _, mock_fn, __):
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH / "util/Rohmaterial",
        excel_full_filepath=TEST_PATH / "util/Zeltlagerfilm 2023.xlsx",
        create_picture_folder=True,
        rating_pictures=4,
    )
    main()
    assert mock_fn.call_count == 10


@patch("src.main.gui_main.MainWindow.util_buttons_status")
@patch("src.main.runner.runners.util_methods.filemethods.copy_file")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_create_rated_picture_folder_errors(mock_input, _, mock_fn, __):
    mock_input.side_effect = [
        UtilTabInput(
            raw_material_folder=TEST_PATH / "util/Rohmaterial",
            excel_full_filepath=TEST_PATH / "ok_empty.xlsx",
            create_picture_folder=True,
            rating_pictures=4,
        ),
        UtilTabInput(
            raw_material_folder=TEST_PATH / "util/Rohmaterial",
            excel_full_filepath=TEST_PATH / "util/Zeltlagerfilm 2023.xlsx",
            create_picture_folder=True,
            rating_pictures=8,
        ),
        UtilTabInput(
            raw_material_folder=TEST_PATH / "util/Rohmaterial",
            excel_full_filepath=TEST_PATH / "duplicated_data.xlsx",
            create_picture_folder=True,
            rating_pictures=4,
        ),
    ]
    main()
    assert mock_fn.call_count == 0


@patch("src.main.gui_main.MainWindow.util_buttons_status")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_statistics(mock_input, _, __):
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH / "util/Rohmaterial",
        excel_full_filepath=TEST_PATH / "util/Zeltlagerfilm 2023.xlsx",
    )
    main()


@patch("src.main.gui_main.MainWindow.util_buttons_status")
@patch("pathlib.Path.mkdir")
@patch("src.main.runner.runners.util_methods.filemethods.copy_file")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_util_input")
def test_run_process_util_full(mock_input, _, mock_fn, __, ___):
    mock_input.return_value = UtilTabInput(
        raw_material_folder=TEST_PATH / "util/Rohmaterial",
        excel_full_filepath=TEST_PATH / "util/Zeltlagerfilm 2023.xlsx",
        do_sections=True,
        do_video_sections=True,
        do_picture_sections=True,
        rating_section=4,
        do_selections=True,
        videos_columns_selection=["Outtakes (x)"],  # 4 Files
        picture_columns_selection=["NZS (x)", "Outtakes (x)"],  # 5 and 4
        marker="x",
        do_search=True,
        videos_columns_search=["Bemerkung"],
        picture_columns_search=["Bemerkung"],
        keywords=["name", "Name", "Test"],
        rating_search=4,
        create_picture_folder=True,
        rating_pictures=4,
    )
    main()
    assert mock_fn.call_count == 17 + 13 + 8 + 10
