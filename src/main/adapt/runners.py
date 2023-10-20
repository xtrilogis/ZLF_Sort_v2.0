import time
from pandas import DataFrame
from pathlib import Path
from typing import Dict, List

from assethandling.basemodels import UtilTabInput, FolderTabInput, RawTabInput, ExcelInput, ExcelConfig, SheetConfig
from assets import constants
from excel.excelmethods import create_emtpy_excel
from foldersetup import folder_setup
from inputhandling.validation import validate_util_paths, validate_setup_path, is_valid_folder, validate_excel_file
from rawmaterial import raw_material as raw
from util import util_methods as eval_
from util.stats import statistics

# !! TODO Add get_data as kwargs


# Todo duplicate with Worker send_result_list
def pretty_send_list(list_: List[str], progress_callback, titel=""):
    progress_callback.emit(titel)
    if list_:
        progress_callback.emit("Probleme:")
    [progress_callback.emit(f"- {x}") for x in list_ if x]


# sample function
def execute_function(progress_callback):
    for n in range(0, 5):
        time.sleep(10)
        progress_callback.emit(str(n * 100 / 4))

    return "Done."


# ### SETUP ### #
def run_folder_setup(inputs: FolderTabInput, progress_callback, get_data) -> str:
    """Create the folder 'Zeltlagerfilm xxxx with all its Subfolders"""
    errors = validate_setup_path(path=inputs.folder)
    if len(errors) == 0:
        progress_callback.emit("Input validiert.")
        folder_setup.create_folder_structure(parent=inputs.folder, date=inputs.date)
        progress_callback.emit("Ordner erfolgreich erstellt.")
    else:
        pretty_send_list(titel="Ordner erstellen", list_=errors, progress_callback=progress_callback)
    return "Ordnerstruktur erfolgreich erstellt"


# ### RAW ### #
def run_correct_structure(inputs: RawTabInput, progress_callback, get_data) -> str:
    run_raw_processes(progress_callback=progress_callback,
                      titel="Korrekte Ordnerstruktur",
                      function=raw.correct_file_structure,
                      raw_material_folder=inputs.raw_material_folder,
                      dst_folder=inputs.raw_material_folder.parent / "New",
                      start=inputs.first_folder_date
                      )
    return "Korrekte Ordnerstruktur abgeschlossen."


def run_rename_files(inputs: RawTabInput, progress_callback, get_data) -> str:
    run_raw_processes(progress_callback=progress_callback,
                      titel="Dateien umbenennen",
                      function=raw.run_rename,
                      raw_material_folder=inputs.raw_material_folder)
    return "Umbenennen abgeschlossen."


def create_excel(inputs: RawTabInput, progress_callback, get_data) -> Path:
    if not is_valid_folder(inputs.excel.excel_folder):
        raise AttributeError("Incorrect Input.")

    progress_callback.emit("Starte Excel erstellen.")
    vid = constants.minimal_columns.copy()
    vid.extend(inputs.excel.video_columns)
    pic = constants.minimal_columns.copy()
    pic.extend(inputs.excel.picture_columns)
    config = ExcelConfig(
        excel_folder=inputs.excel.excel_folder,
        excel_file_name=inputs.excel.excel_file_name,
        sheets=[SheetConfig(name="Videos", columns=vid),
                SheetConfig(name="Bilder", columns=pic)]
    )
    path = create_emtpy_excel(config=config, override=inputs.excel.override)
    progress_callback.emit("Excel-Datei erfolgreich erstellt")
    return path


def run_fill_excel(inputs: RawTabInput, progress_callback, get_data) -> str:
    if isinstance(inputs.excel, ExcelInput):
        path = create_excel(inputs, progress_callback, get_data)
        inputs.excel = path
    run_raw_processes(function=handle_fill_excel,
                      titel="Dateien in Excel schreiben.",
                      progress_callback=progress_callback,
                      excel=inputs.excel,
                      raw_material_folder=inputs.raw_material_folder)

    return "Dateien in Excel schreiben abgeschlossen."


def run_create_picture_folder(inputs: RawTabInput, progress_callback, get_data) -> str:
    run_raw_processes(function=handle_create_picture_folder,
                      titel="Bilderordner erstellen.",
                      progress_callback=progress_callback,
                      folder=inputs.picture_folder,
                      raw_material_folder=inputs.raw_material_folder)
    return "Bilderordner erstellen abgeschlossen."


def run_process_raw_full(inputs: RawTabInput, progress_callback, get_data) -> str:
    mapping = {
        "Korrekte Ordnerstruktur": [inputs.do_structure, run_correct_structure],
        "Umbenennen": [inputs.do_rename, run_rename_files],
        "Dateien in Excel schreiben": [inputs.fill_excel, run_fill_excel],
        "Bilderordner erstellen": [inputs.create_picture_folder, run_create_picture_folder],
    }
    for key, value in mapping.items():
        if value[0]:
            try:
                progress_callback.emit(
                    value[1](inputs=inputs, progress_callback=progress_callback))
            except Exception as e:
                pretty_send_list(titel=f"{key} erstellen.", list_=[str(e)], progress_callback=progress_callback)
    return "Prozessierung abgeschlossen."


# todo utilize get_data
def run_raw_processes(function, progress_callback, titel, **kwargs):
    if not is_valid_folder(kwargs["raw_material_folder"]):
        raise ValueError("Bitte gib einen gültigen Rohmaterial ordner an.")
    progress_callback.emit("Inputs validiert")

    result = function(**kwargs)
    pretty_send_list(titel=titel, list_=result, progress_callback=progress_callback)


def handle_fill_excel(excel: Path, raw_material_folder: Path):
    errors = validate_excel_file(excel)
    if errors:
        errors.insert(0, "Dateien in Excel schreiben.")
        raise ValueError('\n'.join(errors))
    return raw.fill_excel(excel=excel, raw_material_folder=raw_material_folder)


def handle_create_picture_folder(raw_material_folder, folder: Path):
    folder.mkdir()
    if not is_valid_folder(folder):
        raise ValueError("Bitte gib einen gültigen Zielordner an.")

    return raw.create_picture_folder(picture_folder=folder,
                                     raw_material_folder=raw_material_folder)


# ### UTIL ### #
def run_process_util_full(inputs: UtilTabInput, progress_callback, get_data) -> str:
    return run_util_processes(handle_full_execution, inputs, progress_callback)


def run_copy_sections(inputs: UtilTabInput, progress_callback, get_data) -> str:
    return run_util_processes(handle_sections, inputs, progress_callback)


def run_copy_selection(inputs: UtilTabInput, progress_callback, get_data) -> str:
    return run_util_processes(handle_selection, inputs, progress_callback)


def run_search(inputs: UtilTabInput, progress_callback, get_data) -> str:
    return run_util_processes(handle_search, inputs, progress_callback)


def run_create_rated_picture_folder(inputs: UtilTabInput, progress_callback, get_data) -> str:
    return run_util_processes(handle_picture_folder, inputs, progress_callback)


def run_statistics(inputs: UtilTabInput, progress_callback, get_data) -> str:
    progress_callback.emit("Inputs validiert.")
    handle_statistics(raw_path=inputs.raw_material_folder, progress_callback=progress_callback)
    return "Statistik fertig."


# todo utilize get_data
def run_util_processes(function, inputs: UtilTabInput, progress_callback) -> str:
    sheets = validate_and_prepare(raw_material_folder=inputs.raw_material_folder,
                                  excel_full_filepath=inputs.excel_full_filepath)
    progress_callback.emit("Inputs validiert und Excel eingelesen.")

    msg = function(sheets=sheets, inputs=inputs, progress_callback=progress_callback)
    return msg


def validate_and_prepare(raw_material_folder: Path, excel_full_filepath: Path) -> Dict[str, DataFrame]:
    errors = validate_util_paths(raw_material_folder=raw_material_folder,
                                 excel_full_filepath=excel_full_filepath)
    if errors:
        raise ValueError('\n'.join(errors))
    return eval_.prepare_dataframes(excel_file=excel_full_filepath,
                                    raw_path=raw_material_folder)


def handle_full_execution(sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback) -> str:
    mapping = {
        "Abschnitte": [inputs.do_sections, handle_sections],
        "Selektionen": [inputs.do_selections, handle_selection],
        "Suche": [inputs.do_search, handle_search],
        "Bilderordner": [inputs.create_picture_folder, handle_picture_folder]
    }
    for key, value in mapping.items():
        if value[0]:
            try:
                progress_callback.emit(
                    value[1](sheets=sheets, inputs=inputs, progress_callback=progress_callback))
            except Exception as e:
                pretty_send_list(titel=f"{key} erstellen.", list_=[str(e)], progress_callback=progress_callback)
    return "Prozessierung abgeschlossen"


def handle_sections(sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback) -> str:
    for sheet_name, do_section in [("Videos", inputs.do_video_sections),
                                   ("Bilder", inputs.do_picture_sections)]:
        if do_section and not sheets[sheet_name].empty:
            results = eval_.copy_section(df=sheets[sheet_name], rating_limit=inputs.rating_section)
            pretty_send_list(titel=f"{sheet_name}abschnitte erstellt.",
                             list_=results, progress_callback=progress_callback)
    return "Abschnitte abgeschlossen."


def handle_selection(sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback) -> str:
    for sheet_name, columns in [("Videos", inputs.videos_columns_selection),
                                ("Bilder", inputs.picture_columns_selection)]:
        if columns and not sheets[sheet_name].empty:
            result = eval_.copy_selections(df=sheets[sheet_name], raw_path=inputs.raw_material_folder,
                                           columns=columns, marker=inputs.marker)
            pretty_send_list(titel=f"{sheet_name}selektion erstellt.",
                             list_=result, progress_callback=progress_callback)
    return "Selektionen abgeschlossen."


def handle_search(sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback) -> str:
    for sheet_name, columns in [("Videos", inputs.videos_columns_search),
                                ("Bilder", inputs.picture_columns_search)]:
        if columns and not sheets[sheet_name].empty:
            result = eval_.search_columns(df=sheets[sheet_name], columns=columns,
                                          raw_path=inputs.raw_material_folder,
                                          markers=inputs.keywords, rating=inputs.rating_search)
            pretty_send_list(titel=f"{sheet_name}suche erstellt.",
                             list_=result, progress_callback=progress_callback)
    return "Suche abgeschlossen."


def handle_picture_folder(sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback) -> str:
    result = eval_.copy_pictures_with_rating(df=sheets["Bilder"],
                                             raw_path=inputs.raw_material_folder,
                                             rating_limit=inputs.rating_pictures)
    pretty_send_list(titel="Bilderordner", list_=result, progress_callback=progress_callback)
    return "Bilderordner erstellt."


def handle_statistics(raw_path: Path, progress_callback):
    select = raw_path.parent / "Schnittmaterial"

    total_duration, problems, duration_per_day = statistics.get_raw_material_duration(path=raw_path)
    result = [f"Gesamtdauer: {total_duration}"]
    progress_callback.emit("Gesamtdauer ermittelt")

    for day in duration_per_day:
        result.append(f"Dauer am Tag {day[0]} ist {day[1]}.")
    progress_callback.emit("Dauer pro Tag ermittelt")

    result.append(statistics.percent_selected(raw=raw_path, selected=select))
    progress_callback.emit("Verwendeter Anteil ermittelt")

    progress_callback.emit('\n'.join(result))
