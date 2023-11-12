from unittest.mock import patch
from datetime import datetime
from assethandling.basemodels import RawTabInput
from src.main.gui_main import main
from input_mocks import TEST_PATH, excel_input_standard


@patch("src.main.runner.runners.raw_methods.copy_file")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_raw_input")
def test_run_correct_structure(mock_input, sys, mock_fn):
    mock_fn.return_value = None
    paths = ["raw/unstructured/Rohmaterial", "raw/structured1", "raw/structured2"]
    expectation = [28, 56, 84]  # eig aber check structure fehlt [28, 28, 56]
    for num, value in enumerate(paths):
        mock_input.return_value = RawTabInput(
            do_structure=True,
            do_rename=False,
            fill_excel=False,
            create_picture_folder=False,
            raw_material_folder=TEST_PATH / value,
            first_folder_date=datetime(2023, 7, 27),
            excel=excel_input_standard,
            picture_folder=TEST_PATH
            )
        main()
        assert mock_fn.call_count == expectation[num]


@patch("src.main.runner.runners.raw_methods.copy_file")
@patch("sys.exit")
@patch("src.main.gui_main.MainWindow.get_raw_input")
def test_run_correct_structure_errors(mock_input, sys, mock_fn):
    mock_fn.return_value = None
    paths = ["raw/unstructured/Rohmaterial", "raw/structured1", "raw/structured2"]
    expectation = [28, 56, 84]  # eig aber check structure fehlt [28, 28, 56]
    mock_input.return_value = RawTabInput(
        do_structure=True,
        do_rename=False,
        fill_excel=False,
        create_picture_folder=False,
        raw_material_folder=TEST_PATH / "non existent",
        first_folder_date=datetime(2023, 7, 27),
        excel=excel_input_standard,
        picture_folder=TEST_PATH
        )
    main()
    assert mock_fn.call_count == 0

# @mock.patch("PyQt5.QtWidgets.QInputDialog.getText")
# @mock.patch("sys.exit")
# @mock.patch("src.main.gui_main.MainWindow.get_raw_input")
# @mock.patch("pandas.DataFrame.to_excel")
# def test_excel_creation_override(mock_fn, mock_input, sys, mock_input_dialog):
#     mock_input_dialog.return_value = "j", True
#     mock_fn.return_value = None
#     mock_input.return_value = RawTabInput(
#         do_structure=False,
#         do_rename=False,
#         fill_excel=False,
#         create_picture_folder=False,
#         raw_material_folder=input_mocks.TEST_PATH,
#         first_folder_date=datetime.now(),
#         excel=input_mocks.excel_input_manual,
#         picture_folder=input_mocks.TEST_PATH
#     )
#     main()
#     assert mock_fn.call_count == 2
#     assert mock_fn.call_args_list[0][1]["sheet_name"] == "Videos"
#     assert mock_fn.call_args_list[1][1]["sheet_name"] == "Bilder"
#
# @mock.patch("PyQt5.QtWidgets.QInputDialog.getText")
# @mock.patch("sys.exit")
# @mock.patch("src.main.gui_main.MainWindow.get_raw_input")
# @mock.patch("pandas.DataFrame.to_excel")
# def test_excel_creation_no_override(mock_fn, mock_input, sys, mock_input_dialog):
#     mock_input_dialog.return_value = "n", True
#     mock_fn.return_value = None
#     mock_input.return_value = RawTabInput(
#         do_structure=False,
#         do_rename=False,
#         fill_excel=False,
#         create_picture_folder=False,
#         raw_material_folder=input_mocks.TEST_PATH,
#         first_folder_date=datetime.now(),
#         excel=input_mocks.excel_input_manual,
#         picture_folder=input_mocks.TEST_PATH
#     )
#     main()
#     assert mock_fn.call_count == 0
