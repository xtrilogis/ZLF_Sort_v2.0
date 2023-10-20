from typing import Dict
from unittest import mock

from pandas import DataFrame

from excel.excelmethods import create_emtpy_excel, save_sheets_to_excel, load_sheets_as_df, get_columns
from assethandling.basemodels import ExcelConfig, SheetConfig


@mock.patch("excel.excelmethods.save_sheets_to_excel")
def test_create_empty_excel(mock_save, testdata_path):
    config = ExcelConfig(excel_folder=testdata_path,
                         excel_filename="dummy",
                         sheets=[SheetConfig(name="sheet1", columns=["one", "two"])])
    create_emtpy_excel(config=config)
    assert mock_save.called
    assert type(mock_save.call_args.kwargs['sheets']) == dict
    assert len(mock_save.call_args.kwargs['sheets']) == 1
    assert "one" in mock_save.call_args.kwargs['sheets']['sheet1'].columns
    assert "two" in mock_save.call_args.kwargs['sheets']['sheet1'].columns


def test_save_sheets():
    # TODO
    pass


def test_load_sheets():
    # TODO
    pass


def test_get_columns(testdata_path):
    expected = ["Datei", "Tag", "Bewertung", "Abschnitt", "Bewertung", "Bemerkung", "Outtakes"]
    actual = get_columns(testdata_path / "ok_data.xlsx", "Videos")
    for column in expected:
        assert column in actual

