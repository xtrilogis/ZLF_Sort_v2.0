from typing import Dict
from unittest import mock

import pandas as pd
from pandas import DataFrame

from assethandling.basemodels import ExcelConfig, SheetConfig
from excel.excelmethods import (
    create_emtpy_excel,
    get_columns,
    load_sheets_as_df,
    save_sheets_to_excel,
)


@mock.patch("excel.excelmethods.save_sheets_to_excel")
def test_create_empty_excel(mock_save, testdata_path):
    config = ExcelConfig(
        excel_folder=testdata_path,
        excel_filename="dummy",
        sheets=[SheetConfig(name="sheet1", columns=["one", "two"])],
    )
    create_emtpy_excel(config=config)
    assert mock_save.called
    assert type(mock_save.call_args.kwargs["sheets"]) == dict
    assert len(mock_save.call_args.kwargs["sheets"]) == 1
    assert "one" in mock_save.call_args.kwargs["sheets"]["sheet1"].columns
    assert "two" in mock_save.call_args.kwargs["sheets"]["sheet1"].columns


def test_save_sheets(testdata_path):
    sheets = {
        "Sheet1": pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}),
        "Sheet2": pd.DataFrame({"X": [7, 8, 9], "Y": [10, 11, 12]}),
    }
    test_path = testdata_path / "test_excel.xlsx"

    save_sheets_to_excel(sheets, test_path)

    assert test_path.exists()

    df_result = pd.read_excel(test_path, sheet_name=None)
    for sheet_name, df in df_result.items():
        assert sheet_name in sheets
        assert df.equals(sheets[sheet_name])

    # Clean up: Remove the test Excel file
    test_path.unlink()


def test_load_sheets(testdata_path):
    sheets: Dict[str, DataFrame] = load_sheets_as_df(testdata_path / "ok_data.xlsx")
    assert len(sheets.keys()) == 2
    assert "Bilder" in sheets.keys()
    assert "Videos" in sheets.keys()
    assert len(sheets["Videos"].index) == 17
    assert len(sheets["Bilder"].index) == 22
    assert len(sheets["Videos"].columns) == 7
    assert len(sheets["Bilder"].columns) == 9


def test_get_columns(testdata_path):
    expected = [
        "Datei",
        "Tag",
        "Bewertung",
        "Abschnitt",
        "Bewertung",
        "Bemerkung",
        "Outtakes",
    ]
    actual = get_columns(testdata_path / "ok_data.xlsx", "Videos")
    for column in expected:
        assert column in actual
