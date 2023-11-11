from datetime import datetime
from pathlib import Path

from assethandling.basemodels import ExcelInput, ExcelOption, RawTabInput

TEST_PATH = Path.cwd().joinpath("./testData")

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
