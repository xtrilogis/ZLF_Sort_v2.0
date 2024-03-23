from pathlib import Path

import pytest

from inputhandling import validation


def test_validate_folder(testdata_path):
    assert validation.is_valid_folder(Path.cwd())
    assert not validation.is_valid_folder(testdata_path / "non existing Path")
    assert not validation.is_valid_folder(testdata_path / "ok_data.xlsx")


def test_validate_excel_file(testdata_path):
    # should not raise an error
    validation.validate_excel_file(excel_file=testdata_path / "ok_data.xlsx")

    files = ["not_existing.xlsx", "missing_column.xlsx", "missing_sheet.xlsx"]
    for file in files:
        excel_path = testdata_path / file

        with pytest.raises(ValueError):
            validation.validate_excel_file(excel_file=excel_path)


def test_validate_setup(testdata_path):
    good_path = testdata_path
    validation.validate_setup_path(good_path)

    with pytest.raises(ValueError):
        validation.validate_setup_path(testdata_path / "non existing")

    bad_path = testdata_path / "Rohmaterial"
    with pytest.raises(ValueError):
        validation.validate_setup_path(bad_path)


def test_validate_raw(get_raw_input, get_raw_input_non_valid):
    with pytest.raises(ValueError):
        validation.validate_raw(get_raw_input)
    for input_ in get_raw_input_non_valid:
        with pytest.raises(ValueError):
            validation.validate_raw(input_)


def test_validate_util_good(testdata_path):
    files = ["ok_data.xlsx", "ok_empty.xlsx"]
    raw_path = testdata_path / "util/Rohmaterial"
    for file in files:
        excel_path = testdata_path / file

        validation.validate_util_paths(raw_path, excel_path)


def test_validate_util_bad(testdata_path):
    files = ["duplicated_data.xlsx", "missing_column.xlsx", "missing_sheet.xlsx"]
    raw_path_good = testdata_path / "util/Rohmaterial"
    for file in files:
        excel_path_bad = testdata_path / file

        with pytest.raises(ValueError) as e:
            validation.validate_util_paths(raw_path_good, excel_path_bad)


        if "duplicated" in file:
            assert "07-27-Mi_001.MP4" in e.value.args[0]

    good_excel_path = testdata_path / "ok_data.xlsx"
    raw_path_bad = testdata_path / "NichtExistent"
    with pytest.raises(ValueError):
        validation.validate_util_paths(raw_path_bad, good_excel_path)
