import locale
from datetime import datetime
from pathlib import Path

from pytest import fixture

from assethandling.basemodels import ExcelInput, ExcelOption, RawTabInput

ROOT = Path(__file__).parent / "testData"
locale.setlocale(locale.LC_TIME, "de_DE.utf8")


@fixture()
def testdata_path():
    return ROOT

@fixture()
def dummy_folder():
    return ROOT / "dummy folder"

@fixture()
def dummy_file():
    return ROOT / "dummy_file.txt"


@fixture()
def correct_excel():
    return ROOT / "ok_data.xlsx"


@fixture()
def correct_raw():
    return ROOT / "raw/structured1"


@fixture()
def util_material_path():
    return ROOT / "util/Rohmaterial"


@fixture()
def util_excel_path():
    return ROOT / "util/Zeltlagerfilm 2023.xlsx"


class Signals:
    called: int = 0

    def emit(self, text):
        self.called += 1
        print(text)


@fixture()
def pyqt_signal_dummy():
    return Signals()


@fixture()
def get_raw_input():
    mock_excel = ExcelInput(option=ExcelOption.EXISTING, folder=ROOT / "ok_data.xlsx")
    data = {
        "do_structure": True,
        "do_rename": False,
        "fill_excel": True,
        "create_picture_folder": False,
        "raw_material_folder": ROOT / "Rohmaterial",
        "first_folder_date": datetime(2023, 7, 26),
        "excel": mock_excel,
        "picture_folder": ROOT,
    }
    return RawTabInput(**data)


@fixture()
def get_raw_input_non_valid():
    mock_excel = ExcelInput(
        option=ExcelOption.EXISTING,
        folder=ROOT / f"Zeltlagerfilm {datetime.now().date().year}.xlsx",
    )
    data1 = {
        "do_structure": True,
        "do_rename": False,
        "fill_excel": True,
        "create_picture_folder": False,
        "raw_material_folder": ROOT / "Non existing",
        "first_folder_date": datetime(2023, 7, 26),
        "excel": mock_excel,
        "picture_folder": ROOT,
    }

    data2 = {
        "do_structure": True,
        "do_rename": False,
        "fill_excel": True,
        "create_picture_folder": False,
        "raw_material_folder": ROOT / "Non existing",
        "first_folder_date": datetime(2023, 7, 26),
        "excel": mock_excel,
        "picture_folder": ROOT / "non-existing",
    }
    return [RawTabInput(**data1), RawTabInput(**data2)]
