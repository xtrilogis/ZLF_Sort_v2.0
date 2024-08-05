from datetime import datetime
from pathlib import Path
from unittest import mock

from assethandling import constants
from assethandling.basemodels import File, FileType
from fileopertations.filemethods import (
    copy_file,
    create_folder,
    get_file_captured_date,
    get_file_type,
    rename_files,
)


@mock.patch("pathlib.Path.mkdir")
def test_create_folder(mock_mkdir, testdata_path):
    create_folder(testdata_path, "")
    assert not mock_mkdir.called

    create_folder(Path("some/path/"), "test")
    assert mock_mkdir.called
    assert mock_mkdir.call_args.kwargs["parents"]


@mock.patch("shutil.copy")
def test_copy_file(mock_copy, testdata_path, dummy_file):
    copy_file(testdata_path / dummy_file, testdata_path)
    assert not mock_copy.called  # no duplicated Files

    copy_file(testdata_path / dummy_file, testdata_path / "dummy folder")
    assert mock_copy.call_args.kwargs["src"] == testdata_path / dummy_file
    assert (
        mock_copy.call_args.kwargs["dst"]
        == testdata_path / "dummy folder/dummy_file.txt"
    )


@mock.patch("pathlib.Path.rename")
def test_rename_files(mock_rename, pyqt_signal_dummy, testdata_path):
    errors = []
    files = [
        File(
            full_path=testdata_path / "Rohmaterial/a 27.07. Mi/Videos/07-27-Mi_001.MP4",
            date=datetime(2022, 7, 27, 12, 30),
            dst_folder=None,
            type=FileType.VIDEO,
        ),
        File(
            full_path=testdata_path / "Rohmaterial/a 27.07. Mi/Videos/07-27-Mi_002.AVI",
            date=datetime(2022, 7, 27, 12, 31),
            dst_folder=None,
            type=FileType.VIDEO,
        ),
        File(
            full_path=testdata_path / "Rohmaterial/a 27.07. Mi/Videos/07-27-Mi_003.AVI",
            date=datetime(2022, 7, 27, 12, 31),
            dst_folder=None,
            type=FileType.VIDEO,
        ),
    ]

    rename_files(
        folder=testdata_path, all_files=files, progress_callback=pyqt_signal_dummy
    )
    assert mock_rename.call_count == 3
    assert len(errors) == 0
    assert mock_rename.call_args_list[0].args[0].name == "07_27_Mi-001.MP4"
    assert mock_rename.call_args_list[1].args[0].name == "07_27_Mi-002.AVI"
    assert mock_rename.call_args_list[2].args[0].name == "07_27_Mi-003.AVI"


def test_rename_files_bad(testdata_path, pyqt_signal_dummy):
    rename_files(
        folder=testdata_path,
        all_files=[
            File(
                full_path=testdata_path
                / "Rohmaterial/a 27.07. Mi/Videos/07_27_Mi-001.AVI",
                date=datetime(2022, 7, 27, 12, 30),
                dst_folder=None,
                type=FileType.VIDEO,
            )
        ],
        progress_callback=pyqt_signal_dummy,
    )
    assert pyqt_signal_dummy.called == 2

    rename_files(
        folder=testdata_path,
        all_files=[
            File(
                full_path=testdata_path
                / "Rohmaterial/a 27.07. Mi/Videos/07_2_Mi-001.AVI",
                date=datetime(2022, 7, 27, 12, 30),
                dst_folder=None,
                type=FileType.VIDEO,
            )
        ],
        progress_callback=pyqt_signal_dummy,
    )
    assert pyqt_signal_dummy.called == 4


def test_get_file_type():
    for suffix in constants.video_extensions:
        assert get_file_type(Path(f"file{suffix}")) == FileType.VIDEO

    for suffix in constants.image_extensions:
        assert get_file_type(Path(f"file{suffix}")) == FileType.IMAGE

    assert get_file_type(Path("file.xlsx")) == FileType.OTHER


def test_get_captured_date(testdata_path):
    path = testdata_path / "raw/unstructured/Rohmaterial"
    assert get_file_captured_date(
        path / "07-28-Fr_003.MOV", FileType.VIDEO
    ) == datetime(2023, 7, 28, 12, 36, 38)
    assert get_file_captured_date(
        path / "07-27-Do_003.MP4", FileType.VIDEO
    ) == datetime(2023, 7, 27, 8, 16, 56)
    assert get_file_captured_date(
        path / "07-28-Fr_229.JPG", FileType.IMAGE
    ) == datetime(2023, 7, 28, 21, 22, 36)
    assert get_file_captured_date(
        path / "07-28-Fr_230.JPG", FileType.IMAGE
    ) == datetime(2023, 7, 28, 14, 5, 10)
    assert get_file_captured_date(
        path / "08-05-Sa_003.JPG", FileType.IMAGE
    ) == datetime(2023, 8, 5, 1, 47, 24)
