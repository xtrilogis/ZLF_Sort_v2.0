from datetime import datetime
from pathlib import Path

from pytest import fixture
from assethandling.basemodels import RawTabInput


ROOT = Path.cwd() / "testData"


@fixture()
def get_raw_input():
    data = {
            "do_structure": True,
            "do_rename": False,
            "fill_excel": True,
            "create_picture_folder": False,
            "raw_material_folder": ROOT / "Rohmaterial",
            "first_folder_date": datetime(2023, 7, 26),
            "excel_file_fullpath": ROOT / "ok_data.xlsx",
            "picture_folder": ROOT
        }
    return RawTabInput(**data)


@fixture()
def get_raw_input_non_valids():
    data1 = {
            "do_structure": True,
            "do_rename": False,
            "fill_excel": True,
            "create_picture_folder": False,
            "raw_material_folder": ROOT / "Non existing",
            "first_folder_date": datetime(2023, 7, 26),
            "excel_file_fullpath": ROOT / f"Zeltlagerfilm {datetime.now().date().year}.xlsx",
            "picture_folder": ROOT
        }
    data2 = {
        "do_structure": True,
        "do_rename": False,
        "fill_excel": True,
        "create_picture_folder": False,
        "raw_material_folder": ROOT / "Non existing",
        "first_folder_date": datetime(2023, 7, 26),
        "excel_file_fullpath": ROOT / f"Zeltlagerfilm {datetime.now().date().year}.xlsx",
        "picture_folder": ROOT / "non-existing"
    }
    return [RawTabInput(**data1), RawTabInput(**data2)]
