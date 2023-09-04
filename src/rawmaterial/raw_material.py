import locale
from pathlib import Path
from datetime import datetime, timedelta, date
from typing import List, Dict

from pydantic import ValidationError

from assethandling.basemodels import File, FileType
from fileopertations.filemethods import get_file_type, copy_file, get_file_captured_date

locale.setlocale(locale.LC_TIME, 'de_DE.utf8')


def correct_file_structure(raw_material_folder: Path, dst_folder: Path, start: datetime):
    errors = []
    print("Start")
    check_if_right_structure()

    all_files: List[File] = _get_all_files(raw_material_folder=raw_material_folder, errors=errors)
    print("All Files")
    structure: Dict[str | date, Dict[str, List[File]]] = _create_structure(start_date=start)

    _fill_structure(structure=structure, all_files=all_files)
    print("Structure")
    _copy_files(structure=structure, dst_folder=dst_folder, errors=errors)
    print("copied")

    return errors


def check_if_right_structure():
    pass


def _get_all_files(raw_material_folder: Path, errors: List[str]) -> List[File]:
    all_files: List[File] = []
    for element in raw_material_folder.glob('**/*'):
        if element.is_file():
            file_type = get_file_type(element)
            if file_type != FileType.IMAGE and file_type != FileType.VIDEO:
                continue
            datum = get_file_captured_date(element, file_type)

            try:
                all_files.append(File(full_path=element, date=datum, dst_folder=None, type=file_type))
            except ValidationError as e:
                errors.append(f"Datei {element.name}: {str(e)}")
    return all_files


def _create_structure(start_date: datetime) -> Dict[str | date, Dict[str, List[File]]]:
    structure: Dict[str | date, Dict[str, List[File]]] = {}

    for i in range(10):
        structure[start_date.date()]: Dict[str, List[File]] = {FileType.VIDEO.value: [], FileType.IMAGE.value: []}
        start_date += timedelta(days=1)
    structure["Sonstiges"]: Dict[str, List[File]] = {FileType.VIDEO.value: [], FileType.IMAGE.value: []}

    return structure


def _fill_structure(structure: Dict[str | date, Dict[str, List[File]]], all_files: List[File]):
    for file in all_files:
        if file.date.date() in structure.keys():
            structure[file.date.date()][file.type.value].append(file)
        else:
            structure["Sonstiges"][file.type.value].append(file)


def _copy_files(structure: Dict[str | date, Dict[str, List[File]]], dst_folder: Path, errors: List[str]):
    letter = 97
    for key, value in structure.items():
        if isinstance(key, date):
            folder = dst_folder / f'{chr(letter)}-{key.strftime("%d.%m")}-{key.strftime("%A")}'
        else:
            folder = dst_folder / f'{chr(letter)}-{"Sonstiges"}'

        for element in value[FileType.VIDEO.value]:
            try:
                copy_file(element.full_path, folder / "Videos")
            except Exception as e:
                errors.append(f"Problem mit Datei: {element.full_path.name}")

        for element in value[FileType.IMAGE.value]:
            try:
                copy_file(element.full_path, folder / "Bilder")
            except Exception as e:
                errors.append(f"Problem mit Datei: {element.full_path.name}")
        letter += 1


def rename_files():
    # alles mit Datum außer "sonstiges"
    pass


if __name__ == "__main__":
    path = Path("D:/Users/Wisdom/Lernen/Coding_Python/ZLF_Sort_v2.0/TestDateien/Rohmaterial/") # "D:/Users/Wisdom/Allgemein/PJHF/2022_23/Zeltlager/Zeltlagerfilm/Rohmaterial/Sonstiges/Videos/")
    
    # test_file = path / "07-26-Mi_001.JPG" # 08-05-Sa_153.jpg, 08-05-Sa_071.jpeg, 08-05-Sa_081.jpg
    # correct_file_structure(path, Path("D:/Users/Wisdom/Lernen/Coding_Python/ZLF_Sort_v2.0/TestDateien/"), datetime(2022, 7, 27))
    correct_file_structure(Path("D:/Users/Wisdom/Lernen/Coding_Python/ZLF_Sort_v2.0/TestDateien/roh/"),
                           Path("D:/Users/Wisdom/Lernen/Coding_Python/TestDateien/"),
                           datetime(2023, 7, 26))
