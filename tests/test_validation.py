from pathlib import Path

from src.inputhandling import validation


def test_validate_folder(testdata_path):
    assert validation.is_valid_folder(Path.cwd())
    assert not validation.is_valid_folder(testdata_path / "non existing Path")
    assert not validation.is_valid_folder(testdata_path / "ok_data.xlsx")


def test_validate_excel_file(testdata_path):
    errors = validation.validate_excel_file(excel_file=testdata_path / "ok_data.xlsx")
    assert len(errors) == 0
    files = ["not_existing.xlsx", "missing_column.xlsx", "missing_sheet.xlsx"]
    for file in files:
        excel_path = testdata_path / file

        errors = validation.validate_excel_file(excel_file=excel_path)
        assert len(errors) != 0


def test_validate_setup(testdata_path):
    good_path = testdata_path
    errors = validation.validate_setup_path(good_path)
    assert len(errors) == 0

    not_existing = Path("C:/some/path")
    errors = validation.validate_setup_path(not_existing)
    assert len(errors) != 0

    bad_path = testdata_path / "Rohmaterial"
    errors = validation.validate_setup_path(bad_path)
    assert len(errors) != 0


def test_validate_raw(get_raw_input, get_raw_input_non_valids):
    assert len(validation.validate_raw(get_raw_input)) == 0
    for input_ in get_raw_input_non_valids:
        assert len(validation.validate_raw(input_)) != 0


def test_validate_util_good(testdata_path):
    files = ["ok_data.xlsx", "ok_empty.xlsx"]
    raw_path = testdata_path / "Rohmaterial"
    for file in files:
        excel_path = testdata_path / file

        errors = validation.validate_util_paths(raw_path,
                                                excel_path)
        assert len(errors) == 0


def test_validate_util_bad(testdata_path):
    files = ["duplicated_data.xlsx", "missing_column.xlsx", "missing_sheet.xlsx"]
    raw_path = testdata_path / "Rohmaterial"
    for file in files:
        excel_path = testdata_path / file

        errors = validation.validate_util_paths(raw_path,
                                                excel_path)
        assert len(errors) != 0
        if "duplicated" in file:
            assert "07-27-Mi_001.MP4" in errors

    good_excel_path = testdata_path / "ok_data.xlsx"
    raw_path = testdata_path / "NichtExistent"
    errors = validation.validate_util_paths(raw_path,
                                            good_excel_path)
    assert len(errors) != 0
