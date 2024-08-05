from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List

from pydantic import ValidationError

from assethandling.basemodels import File, FileType

from fileopertations.filemethods import (
    copy_file,
    create_folder,
    get_file_captured_date,
    get_file_type
)

# @mock.patch("rawmaterial.raw_material.copy_file")
# def test_correct_folder_structure(mock_copy, correct_raw, testdata_path):
#     mock_callback = MagicMock()
#     mock_get_data = MagicMock(return_value="Nein")
#     correct_file_structure(
#         correct_raw, datetime(2023, 7, 27), mock_callback, mock_get_data
#     )
#     assert mock_copy.call_count == 29
#     f = str(testdata_path)
#     assert "a 27.07.-Do\\Bilder\\07-27-Do_001.jpg" in str(
#         mock_copy.call_args_list[0].args[0]
#     )
#     assert "New\\a-27.07-Donnerstag\\Bilder" in str(mock_copy.call_args_list[0].args[1])
#     assert "Sonstiges\\Bilder\\08-05-Sa_003.JPG" in str(
#         mock_copy.call_args_list[22].args[0]
#     )
#     assert "New\\j-05.08-Samstag\\Bilder" in str(mock_copy.call_args_list[22].args[1])
#     shutil.rmtree(testdata_path / "raw/New")


# @mock.patch("rawmaterial.raw_material.copy_file")
# def test_correct_folder_structure2(mock_copy, correct_raw, testdata_path):
#     mock_callback = MagicMock()
#     mock_get_data = MagicMock(return_value="Nein")
#     result = correct_file_structure(
#         testdata_path / "raw/unstructured/Rohmaterial",
#         datetime(2023, 7, 27),
#         mock_callback,
#         mock_get_data,
#     )
#     assert result
#
#     correct_file_structure(
#         testdata_path / "raw/structured2",
#         datetime(2023, 7, 27),
#         mock_callback,
#         mock_get_data,
#     )
#     assert mock_copy.call_count == 29
#     f = str(testdata_path)
#     assert "a 27.07.-Do\\07-27-Do_001.jpg" in str(mock_copy.call_args_list[0].args[0])
#     assert "New\\a-27.07-Donnerstag\\Bilder" in str(mock_copy.call_args_list[0].args[1])
#     assert "Sonstiges\\08-05-Sa_003.JPG" in str(mock_copy.call_args_list[22].args[0])
#     assert "New\\j-05.08-Samstag\\Bilder" in str(mock_copy.call_args_list[22].args[1])
#     shutil.rmtree(testdata_path / "raw/New")



def correct_file_structure(
    raw_material_folder: Path,
    start: datetime,
    progress_callback,
    get_data,
):
    dst_folder = create_folder(raw_material_folder.parent, "New")

    if [x for x in dst_folder.iterdir()]:
        response = get_data(
            text=f"Im Zielordner {dst_folder.parent}/{dst_folder.name}\n"
            f"existieren bereits Dateien/Ordner.\n"
            f"Sollen diese Überschrieben werden? j/n"
        )
        if response != "Ja":
            progress_callback.emit("Abbruch. Zielordner nicht leer")
            return

    all_files: List[File] = _get_all_files(
        raw_material_folder=raw_material_folder, progress_callback=progress_callback
    )
    progress_callback.emit("Dateien eingelesen.")

    structure: Dict[str | date, Dict[str, List[File]]] = _create_structure(
        start_date=start
    )
    _fill_structure(structure=structure, all_files=all_files)
    progress_callback.emit("Struktur erstellt.")

    # _check_if_right_structure(structure, raw_material_folder, progress_callback)
    _copy_file_structure(
        structure=structure, dst_folder=dst_folder, progress_callback=progress_callback
    )


def _get_all_files(raw_material_folder: Path, progress_callback) -> List[File]:
    all_files: List[File] = []
    for element in raw_material_folder.glob("**/*"):
        _add_file_object(
            file=element, all_files=all_files, progress_callback=progress_callback
        )
    return all_files


def _add_file_object(file: Path, all_files: List[File], progress_callback):
    if not file.is_file():
        return

    file_type = get_file_type(file)
    if file_type != FileType.IMAGE and file_type != FileType.VIDEO:
        return
    datum = get_file_captured_date(file, file_type)

    try:
        all_files.append(
            File(full_path=file, date=datum, dst_folder=None, type=file_type)
        )
    except ValidationError as e:
        progress_callback.emit(f"Fehler: Datei {file.name} \n {str(e)}")


def _create_structure(start_date: datetime) -> Dict[str | date, Dict[str, List[File]]]:
    structure: Dict[str | date, Dict[str, List[File]]] = {}

    for i in range(10):
        structure[start_date.date()]: Dict[str, List[File]] = {
            FileType.VIDEO.value: [],
            FileType.IMAGE.value: [],
        }
        start_date += timedelta(days=1)
    structure["Sonstiges"]: Dict[str, List[File]] = {
        FileType.VIDEO.value: [],
        FileType.IMAGE.value: [],
    }

    return structure


def _fill_structure(
    structure: Dict[str | date, Dict[str, List[File]]], all_files: List[File]
):
    for file in all_files:
        if file.date.date() in structure.keys():
            structure[file.date.date()][file.type.value].append(file)
        else:
            structure["Sonstiges"][file.type.value].append(file)


def _copy_file_structure(
    structure: Dict[str | date, Dict[str, List[File]]],
    dst_folder: Path,
    progress_callback,
):
    letter = 97
    copied_files_nr: int = 0
    for key, value in structure.items():
        if isinstance(key, date):
            folder = (
                dst_folder
                / f'{chr(letter)}-{key.strftime("%d.%m")}-{key.strftime("%A")}'
            )
        else:
            folder = dst_folder / f'{chr(letter)}-{"Sonstiges"}'

        copied_files_nr += _copy_files(
            value[FileType.IMAGE.value], folder / "Bilder", progress_callback
        )
        copied_files_nr += _copy_files(
            value[FileType.VIDEO.value], folder / "Videos", progress_callback
        )

        letter += 1
    progress_callback.emit(f"{copied_files_nr} Dateien kopiert.")


def _copy_files(elements: List[File], folder_name: Path, progress_callback) -> int:
    copied_files_nr: int = 0
    for element in elements:
        try:
            copy_file(element.full_path, folder_name)
            copied_files_nr += 1
        except Exception as e:
            progress_callback.emit(
                f"Fehler: Datei {element.full_path.name} konnte nicht kopiert werden."
            )
    return copied_files_nr
