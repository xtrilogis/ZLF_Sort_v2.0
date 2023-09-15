from unittest import mock
from util.util_methods import prepare_dataframes, copy_section, \
    copy_selections, search_columns, copy_pictures_with_rating
from excel.excelmethods import load_sheets_as_df
# mock_copy_file assert calls with right argument
# dummy_df, good and bad
# test with mock_copy_file mit raise FileNotFound

def test_prepare_df():
    # Todo implementation
    pass


@mock.patch("util.util_methods.filemethods.copy_file")
def test_copy_section():
    # Todo implementation
    pass


@mock.patch("util.util_methods.filemethods.copy_file")
def test_copy_selections():
    # Todo implementation
    pass


@mock.patch("util.util_methods.filemethods.copy_file")
def test_search_columns():
    # Todo implementation
    pass


@mock.patch("util.util_methods.filemethods.copy_file")
def test_copy_pictures_with_rating(mock_copy, correct_raw, correct_excel):
    df = prepare_dataframes(correct_excel, correct_raw)['Bilder']
    copy_pictures_with_rating(df=df, raw_path=correct_raw, rating_limit=4)

    assert mock_copy.called
    assert mock_copy.call_count == 12


@mock.patch("util.util_methods.filemethods.copy_file")
def test_copy_pictures_with_rating_bad(mock_copy, correct_raw, testdata_path):
    df = prepare_dataframes(testdata_path / "duplicated_data.xlsx", correct_raw)['Bilder']
    errors = copy_pictures_with_rating(df=df, raw_path=correct_raw, rating_limit=4)

    assert mock_copy.called
    assert mock_copy.call_count == 2
    assert len(errors) == 1
