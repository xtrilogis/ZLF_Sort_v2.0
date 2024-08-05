import shutil
from typing import Dict
from unittest import mock
from unittest.mock import MagicMock

import pandas as pd
import pytest

from util.util_methods import (
    copy_pictures_with_rating,
    copy_section,
    copy_selections,
    create_statistics,
    prepare_dataframes,
    search_columns,
)


def test_prepare_df(util_excel_path, util_material_path, testdata_path):
    result: Dict[str, pd.DataFrame] = prepare_dataframes(
        excel_file=util_excel_path, raw_path=util_material_path
    )

    assert len(result.keys()) == 2
    assert "Dateipfad" in result["Bilder"].columns
    assert "Dateipfad" in result["Videos"].columns
    expected = (
        "src\\tests\\testData\\util\\Rohmaterial\\b 27.07.-Do\\Bilder\\07_27_Do-001.jpg"
    )
    assert expected in str(result["Bilder"].loc[1, "Dateipfad"])
    with pytest.raises(ValueError):
        prepare_dataframes(
            excel_file=testdata_path / "ok_empty.xlsx", raw_path=util_material_path
        )


@mock.patch("util.util_methods.filemethods.copy_file")
def test_copy_section(mock_copy, util_excel_path, util_material_path):
    result: Dict[str, pd.DataFrame] = prepare_dataframes(
        excel_file=util_excel_path, raw_path=util_material_path
    )
    mock_callback = MagicMock()

    copy_section(result["Bilder"], 4, mock_callback)
    assert mock_copy.call_count == 10
    assert mock_callback.emit.call_count == 1

    dest_path = util_excel_path.parent / "Schnittmaterial"
    assert dest_path.exists()

    shutil.rmtree(dest_path)


@mock.patch("util.util_methods.filemethods.copy_file")
def test_copy_selections(mock_copy, util_excel_path, util_material_path):
    result: Dict[str, pd.DataFrame] = prepare_dataframes(
        excel_file=util_excel_path, raw_path=util_material_path
    )
    mock_callback = MagicMock()
    copy_selections(
        result["Bilder"], util_material_path, ["Outtakes (x)"], "x", mock_callback
    )
    assert mock_copy.call_count == 4
    assert mock_callback.emit.call_count == 1
    copy_selections(
        result["Bilder"], util_material_path, ["Non existing"], "x", mock_callback
    )
    assert mock_callback.emit.call_count == 2


@mock.patch("util.util_methods.filemethods.copy_file")
def test_search_columns(mock_copy, util_excel_path, util_material_path):
    result: Dict[str, pd.DataFrame] = prepare_dataframes(
        excel_file=util_excel_path, raw_path=util_material_path
    )
    mock_callback = MagicMock()
    search_columns(
        result["Bilder"], util_material_path, ["Bemerkung"], ["Test"], 4, mock_callback
    )
    assert mock_copy.call_count == 4


@mock.patch("util.util_methods.filemethods.copy_file")
def test_copy_pictures_with_rating(mock_copy, util_excel_path, util_material_path):
    result: Dict[str, pd.DataFrame] = prepare_dataframes(
        excel_file=util_excel_path, raw_path=util_material_path
    )
    mock_callback = MagicMock()
    copy_pictures_with_rating(result["Bilder"], util_material_path, 4, mock_callback)
    assert mock_copy.call_count == 10
    assert mock_callback.emit.call_count == 1


def test_create_statistics(util_material_path):
    mock_callback = MagicMock()
    create_statistics(util_material_path, mock_callback)
    assert mock_callback.emit.call_count == 4
    assert (
        "Gesamtdauer: 00:20:30\nDauer am Tag b 27.07.-Do ist 00:03:02.\nDauer am Tag c 28.07.-Fr ist 00:17:09.\nDauer am Tag Sonstiges ist 00:00:18.\n0 von 28 benutzt. (0.0%)"
        == mock_callback.emit.call_args_list[-1].args[0]
    )
