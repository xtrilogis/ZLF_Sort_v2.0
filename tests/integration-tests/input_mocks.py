from datetime import datetime
from pathlib import Path

from assethandling.basemodels import ExcelInput, ExcelOption, RawTabInput, UtilTabInput

TEST_PATH = Path.cwd().joinpath("./testData")
TEST_DATE = datetime(2023, 10, 5)

excel_input_standard: ExcelInput = ExcelInput(
    option=ExcelOption.CREATE,
    folder=TEST_PATH,
)

excel_input_manual: ExcelInput = ExcelInput(
    option=ExcelOption.CREATE,
    name=f"Zeltlagerfilm custom.xlsx",
    folder=TEST_PATH,
    video_columns=["column1"],
    picture_columns=["column2"]
)

excel_input_existing: ExcelInput = ExcelInput(
    option=ExcelOption.EXISTING,
    name="existing.xlsx",
    folder=TEST_PATH,
)

rti_single_button = RawTabInput(
    do_structure=False,
    do_rename=False,
    fill_excel=False,
    create_picture_folder=False,
    raw_material_folder=TEST_PATH,
    first_folder_date=datetime.now(),
    excel=excel_input_standard,
    picture_folder=TEST_PATH
)

no_input_util = UtilTabInput(
    raw_material_folder=TEST_PATH,
    excel_full_filepath=TEST_PATH / "ok_data.xlsx",
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
    keywords=[],
    rating_search=0,
    create_picture_folder= False,
    rating_pictures=0
)
