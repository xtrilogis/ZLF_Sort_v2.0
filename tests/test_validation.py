from pathlib import Path

from src.inputhandling import validation

ROOT = Path.cwd() / "testData"


def test_validate_setup():
    good_path = ROOT
    valid, errors = validation.validate_setup_path(ROOT)
    assert valid

    not_existing = Path("C:/some/path")
    valid, errors = validation.validate_setup_path(not_existing)
    assert not valid

    bad_path = ROOT / "Rohmaterial"
    valid, errors = validation.validate_setup_path(bad_path)
    assert not valid


def test_validate_util_good():
    files = ["ok_data.xlsx", "ok_empty.xlsx"]
    raw_path = ROOT / "Rohmaterial"
    for file in files:
        excel_path = ROOT / file

        valid, errors = validation.validate_util_paths(raw_path,
                                                       excel_path)
        assert valid
        assert len(errors) == 0


def test_validate_util_bad():
    files = ["duplicated_data.xlsx", "missing_column.xlsx", "missing_sheet.xlsx"]
    raw_path = ROOT / "Rohmaterial"
    for file in files:
        excel_path = ROOT / file

        valid, errors = validation.validate_util_paths(raw_path,
                                                       excel_path)
        assert not valid
        assert len(errors) != 0
        if "duplicated" in file:
            assert "07-27-Mi_001.MP4" in errors

    good_excel_path = ROOT / "ok_data.xlsx"
    raw_path = ROOT / "NichtExistent"
    valid, errors = validation.validate_util_paths(raw_path,
                                                   good_excel_path)
    assert not valid
    assert len(errors) != 0
