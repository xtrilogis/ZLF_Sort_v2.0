import locale
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta, date
from typing import List, Dict
from pydantic import ValidationError

from assethandling.basemodels import File, FileType
from assets import constants
from excel.excelmethods import load_sheets_as_df, save_sheets_to_excel, create_emtpy_excel
from fileopertations.filemethods import get_file_type, copy_file, get_file_captured_date, rename_files

locale.setlocale(locale.LC_TIME, 'de_DE.utf8')


def correct_file_structure(raw_material_folder: Path, dst_folder: Path, start: datetime, get_data) -> List[str]:
    errors = []
    if [x for x in dst_folder.iterdir()]:
        response = get_data(text=f"Im Zielordner {dst_folder.parent}/{dst_folder.name}\n"
                                 f"existieren bereits Dateien/Ordner.\n"
                                 f"Sollen diese Überschrieben werden? j/n")
        if response.lower != "j":
            return ["Abbruch. Zielordner nicht leer"]

    all_files: List[File] = _get_all_files(raw_material_folder=raw_material_folder, errors=errors)
    structure: Dict[str | date, Dict[str, List[File]]] = _create_structure(start_date=start)


    _fill_structure(structure=structure, all_files=all_files)

    # _check_if_right_structure(structure, raw_material_folder)
    _copy_file_structure(structure=structure, dst_folder=dst_folder, errors=errors)
    # feat: Feedback how many files were copied
    return errors


def _check_if_right_structure(structure, raw_material_folder: Path):
    # Todo
    # adapt test
    # if errors len < z.B. 10 User Fragen, ob das imm Rahmen ist oder ob verändert werden soll
    read_structure, errors = _read_structure(raw_material_folder=raw_material_folder)
    for key, value in read_structure.items():
        pass
    # structure == read_structure compare keys().length, compare if same amount of images and videos per Day
    pass

def _read_structure(raw_material_folder: Path):
    errors = []
    structure = {}
    for a in raw_material_folder.iterdir():
        if a.is_dir(): # Tage
            structure[a.name] = {"Bilder": [], "Videos": []}
            for b in a.iterdir():
                if b.is_file(): # Videos | Bilder
                    errors.append(f"Datei {b.parent}/{b.name} außerhalb der richtigen Struktur.")
                    pass # Fehler
                if b.is_dir():
                    for c in b.iterdir():
                        if c.is_file(): # tatsächliche files
                            _add_file_object(file=c, all_files=structure[a.name][b.name], errors=errors)
                        if c.is_dir():
                            errors.append(f"Ordner {c.parent.parent}/{c.parent}/{c.name} außerhalb der richtigen Struktur.")

    return structure, errors

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


def _copy_file_structure(structure: Dict[str | date, Dict[str, List[File]]], dst_folder: Path, errors: List[str]):
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
    # todo: msg when no files renamed
    # todo: reduce duplicated code
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

def create_excel(config, progress_callback, get_data):
    try:
        path = create_emtpy_excel(config=config)
        progress_callback.emit("Excel-Datei erfolgreich erstellt")
        return path
    except FileExistsError:
        response: str = get_data(text="Excel existiert bereits. Soll sie überschrieben werden? j/n")
        if response.lower() == "j":
            path = create_emtpy_excel(config=config, override=True)
            progress_callback.emit("Excel-Datei erfolgreich erstellt")
            return path
        progress_callback.emit("Excel wurde nicht erstellt, da die Datei bereits vorhanden ist.")

def fill_excel(excel: Path, raw_material_folder: Path) -> List[str]:
    errors: List[str] = []
    sheets: Dict[str, pd.DataFrame] = load_sheets_as_df(excel)
    if not sheets["Videos"].empty or not sheets["Bilder"].empty:
        # feat: ask if Excel should be overwritten
        raise ValueError("Die Excel enthält bereits Daten.")

    for element in raw_material_folder.glob('**/*'):
        if _is_folder_with_material(element):
            _fill_sheets(folder=element, sheets=sheets, errors=errors)

    save_sheets_to_excel(sheets=sheets, path=excel)
    return errors


def _fill_sheets(folder: Path, sheets: Dict[str, pd.DataFrame], errors: List[str]):
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
                    sheets["Bilder"].loc[len(sheets["Bilder"]), "Datei"] = folder.parent.name
                    picture_folder_written = True
                sheets["Bilder"].loc[len(sheets["Bilder"]), "Datei"] = child.name
        except IndexError as e:
            errors.append(child.name)


def create_picture_folder(picture_folder: Path, raw_material_folder: Path) -> List[str]:
    # feat: check if folder contains elements and then ask for handling
    errors: List[str] = []
    for element in raw_material_folder.glob('**/*'):
        if element.suffix.upper() in constants.image_extensions:
            try:
                copy_file(element, picture_folder)
            except (FileNotFoundError, FileExistsError) as e:
                errors.append(element.name)
    return errors
