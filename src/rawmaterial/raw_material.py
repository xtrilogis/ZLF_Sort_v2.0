import locale
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta, date
from typing import List, Dict
from pydantic import ValidationError

from assethandling.basemodels import File, FileType
from assets import constants
from excel.excelmethods import load_sheets_as_df, save_sheets_to_excel
from fileopertations.filemethods import get_file_type, copy_file, get_file_captured_date, rename_files

locale.setlocale(locale.LC_TIME, 'de_DE.utf8')


def correct_file_structure(raw_material_folder: Path, dst_folder: Path, start: datetime) -> List[str]:
    errors = []
    check_if_right_structure()

    all_files: List[File] = _get_all_files(raw_material_folder=raw_material_folder, errors=errors)
    structure: Dict[str | date, Dict[str, List[File]]] = _create_structure(start_date=start)

    _fill_structure(structure=structure, all_files=all_files)
    _copy_files(structure=structure, dst_folder=dst_folder, errors=errors)

    return errors


def check_if_right_structure():
    pass


def _get_all_files(raw_material_folder: Path, errors: List[str]) -> List[File]:
    all_files: List[File] = []
    for element in raw_material_folder.glob('**/*'):
        _add_file_object(file=element, all_files=all_files, errors=errors)
    return all_files


def _add_file_object(file: Path, all_files: List[File], errors: List[str]):
    if not file.is_file():
        return

    file_type = get_file_type(file)
    if file_type != FileType.IMAGE and file_type != FileType.VIDEO:
        return
    datum = get_file_captured_date(file, file_type)

    try:
        all_files.append(File(full_path=file, date=datum, dst_folder=None, type=file_type))
    except ValidationError as e:
        errors.append(f"Datei {file.name}: {str(e)}")


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


def run_rename(raw_material_folder: Path) -> List[str]:
    errors: List[str] = []
    if _is_folder_with_material(raw_material_folder):
        all_files: List[File] = []
        for child in raw_material_folder.iterdir():
            _add_file_object(file=child, all_files=all_files, errors=errors)
        all_files.sort(key=lambda x: x.date, reverse=False)

        rename_files(folder=raw_material_folder, all_files=all_files, errors=errors)

    for element in raw_material_folder.glob('**/*'):
        if _is_folder_with_material(element):
            all_files: List[File] = []
            for child in element.iterdir():
                _add_file_object(file=child, all_files=all_files, errors=errors)
            all_files.sort(key=lambda x: x.date, reverse=False)

            rename_files(folder=element, all_files=all_files, errors=errors)
    return errors


def _is_folder_with_material(path: Path) -> bool:
    if not path.is_dir():
        return False
    for element in path.iterdir():
        if element.suffix.upper() in constants.video_extensions or element.suffix.upper() in constants.image_extensions:
            return True
    return False


def fill_excel(excel: Path, raw_material_folder: Path) -> List[str]:
    errors: List[str] = []
    sheets: Dict[str, pd.DataFrame] = load_sheets_as_df(excel)
    if not sheets["Videos"].empty or not sheets["Bilder"].empty:
        raise ValueError("Die Excel enthält bereits Daten.")

    for element in raw_material_folder.glob('**/*'):
        if _is_folder_with_material(element):
            _add_child_files(folder=element, sheets=sheets, errors=errors)

    save_sheets_to_excel(sheets=sheets, path=excel)
    return errors


def _add_child_files(folder: Path, sheets: Dict[str, pd.DataFrame], errors: List[str]):
    picture_folder_written = False
    video_folder_written = False
    for child in folder.iterdir():
        try:
            if child.suffix.upper() in constants.video_extensions:
                if not video_folder_written:
                    sheets["Videos"].loc[len(sheets["Videos"]), "Datei"] = folder.parent.name
                    video_folder_written = True
                sheets["Videos"].loc[len(sheets["Videos"]), "Datei"] = child.name

            if child.suffix.upper() in constants.image_extensions:
                if not picture_folder_written:
                    sheets["Bilder"].loc[len(sheets["Bilder"]), "Datei"] = folder.name
                    picture_folder_written = True
                sheets["Bilder"].loc[len(sheets["Bilder"]), "Datei"] = child.name
        except IndexError as e:
            errors.append(child.name)


def create_picture_folder(picture_folder: Path, raw_material_folder: Path) -> List[str]:
    errors: List[str] = []
    for element in raw_material_folder.glob('**/*'):
        if element.suffix.upper() in constants.image_extensions:
            try:
                copy_file(element, picture_folder)
            except (FileNotFoundError, FileExistsError) as e:
                errors.append(element.name)
    return errors
