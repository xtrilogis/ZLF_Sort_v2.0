import time

from pathlib import Path
from typing import Dict, List

from assethandling.basemodels import UtilTabInput, FolderTabInput, RawTabInput, ExcelInput, ExcelConfig, SheetConfig, \
    ExcelOption
from assets import constants
from src.main.connectors import raw_connector, util_connector

from inputhandling.validation import validate_util_paths, validate_setup_path, is_valid_folder
# todo this file should only contain runners/wrapper meaning
# - functions called from a button click
# - functions take input, progress_callback, get_data
# - return a String indicating witch parte has been processed
# these functions filter the input for further processing (and do some validation?)
# acts like an interface
from excel.excelmethods import create_emtpy_excel
from foldersetup import folder_setup
from rawmaterial import raw_material as raw
from util import util_methods as eval_
from pandas import DataFrame


# Todo duplicate with Worker send_result_list
# use errors Signal
def pretty_send_problems(list_: List[str], progress_callback, titel=""):
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
    # todo move into a connector?
    errors = validate_setup_path(path=inputs.folder)
    if len(errors) == 0:
        progress_callback.emit("Input validiert.")
        folder_setup.create_folder_structure(parent=inputs.folder, date=inputs.date)
        progress_callback.emit("Ordner erfolgreich erstellt.")
    else:
        pretty_send_problems(titel="Ordner erstellen", list_=errors, progress_callback=progress_callback)
    return "Ordnerstruktur erfolgreich erstellt"


# ### RAW ### #
def raw_process(titel):
    def decor(func):
        def wrap(*args, **kwargs):
            progress_callback = kwargs["progress_callback"]

            if not is_valid_folder(kwargs["inputs"].raw_material_folder):
                raise ValueError("Bitte gib einen gültigen Rohmaterial ordner an.")
            progress_callback.emit("Inputs validiert")

            result = func(*args, **kwargs)
            pretty_send_problems(titel=titel, list_=result, progress_callback=progress_callback)
            return f"{titel} abgeschlossen."

        return wrap

    return decor


@raw_process("Korrekte Ordnerstruktur")
def run_correct_structure(inputs: RawTabInput, **kwargs) -> List[str]:
    return raw.correct_file_structure(raw_material_folder=inputs.raw_material_folder,
                                      dst_folder=inputs.raw_material_folder.parent / "New",
                                      start=inputs.first_folder_date)


@raw_process("Dateien umbenennen")
def run_rename_files(inputs: RawTabInput, **kwargs) -> List[str]:
    return raw.run_rename(raw_material_folder=inputs.raw_material_folder)


def run_create_excel(inputs: RawTabInput, progress_callback, get_data, **kwargs) -> Path:
    if inputs.excel.option != ExcelOption.CREATE:
        raise AttributeError("Can't call create Excel for existing Excel.")

    if not is_valid_folder(inputs.excel.folder):
        raise AttributeError("The given folder is not a valid folder.")

    progress_callback.emit("Starte Excel erstellen.")
    path = raw_connector.handle_create_excel(config_=inputs.excel,
                                             get_data=get_data,
                                             progress_callback=progress_callback)
    return path


@raw_process("Dateien in Excel schreiben")
def run_fill_excel(inputs: RawTabInput, progress_callback, get_data, **kwargs) -> List[str]:
    if inputs.excel.option == ExcelOption.CREATE:
        run_create_excel(inputs, progress_callback, get_data)
    return raw_connector.handle_fill_excel(excel=inputs.excel.full_path,
                                           raw_material_folder=inputs.raw_material_folder)


@raw_process("Bilderordner erstellen")
def run_create_picture_folder(inputs: RawTabInput, **kwargs) -> List[str]:
    return raw_connector.handle_create_picture_folder(raw_material_folder=inputs.raw_material_folder,
                                                      folder=inputs.picture_folder)


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
                result = value[1](inputs=inputs, progress_callback=progress_callback, get_data=get_data)
                progress_callback.emit(result)
            except Exception as e:
                pretty_send_problems(titel=f"{key} erstellen.", list_=[str(e)], progress_callback=progress_callback)
    return "Prozessierung abgeschlossen."


# ### UTIL ### #
def util_process():
    def decor(func):
        def wrap(inputs: UtilTabInput, progress_callback, get_data, *args, **kwargs):

            sheets = validate_and_prepare(raw_material_folder=inputs.raw_material_folder,
                                          excel_full_filepath=inputs.excel_full_filepath)
            progress_callback.emit("Inputs validiert und Excel eingelesen.")

            msg = func(sheets=sheets, inputs=inputs, progress_callback=progress_callback)
            return msg
        return wrap
    return decor


def validate_and_prepare(raw_material_folder: Path, excel_full_filepath: Path) -> Dict[str, DataFrame]:
    errors = validate_util_paths(raw_material_folder=raw_material_folder,
                                 excel_full_filepath=excel_full_filepath)
    if errors:
        raise ValueError('\n'.join(errors))
    return eval_.prepare_dataframes(excel_file=excel_full_filepath,
                                    raw_path=raw_material_folder)


@util_process()
def run_process_util_full(sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback) -> str:
    mapping = {
        "Abschnitte": [inputs.do_sections, util_connector.handle_sections],
        "Selektionen": [inputs.do_selections, util_connector.handle_selection],
        "Suche": [inputs.do_search, util_connector.handle_search],
        "Bilderordner": [inputs.create_picture_folder, util_connector.handle_picture_folder]
    }
    for key, value in mapping.items():
        if value[0]:
            try:
                progress_callback.emit(
                    value[1](sheets=sheets, inputs=inputs, progress_callback=progress_callback))
            except Exception as e:
                pretty_send_problems(titel=f"{key} erstellen.", list_=[str(e)], progress_callback=progress_callback)
    return "Prozessierung abgeschlossen"


@util_process()
def run_copy_sections(sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback) -> str:
    return util_connector.handle_sections(sheets=sheets, inputs=inputs, progress_callback=progress_callback)


@util_process()
def run_copy_selection(sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback) -> str:
    return util_connector.handle_selection(sheets=sheets, inputs=inputs, progress_callback=progress_callback)


@util_process()
def run_search(sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback) -> str:
    return util_connector.handle_search(sheets=sheets, inputs=inputs, progress_callback=progress_callback)


@util_process()
def run_create_rated_picture_folder(sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback) -> str:
    return util_connector.handle_picture_folder(sheets=sheets, inputs=inputs, progress_callback=progress_callback)


def run_statistics(inputs: UtilTabInput, progress_callback, get_data) -> str:
    progress_callback.emit("Inputs validiert.")
    util_connector.handle_statistics(raw_path=inputs.raw_material_folder, progress_callback=progress_callback)
    return "Statistik fertig."
