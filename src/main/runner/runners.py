from pathlib import Path
from typing import Dict, List

from assethandling.basemodels import UtilTabInput, FolderTabInput, RawTabInput, ExcelInput, ExcelConfig, SheetConfig, \
    ExcelOption
from assets import constants

from inputhandling.validation import validate_util_paths, validate_setup_path, is_valid_folder, validate_excel_file
from excel.excelmethods import create_emtpy_excel
from foldersetup import folder_setup as setup_methods
from rawmaterial import raw_material as raw_methods
from util import util_methods as util_methods
from pandas import DataFrame


# ### SETUP ### #
def run_folder_setup(inputs: FolderTabInput, progress_callback, get_data) -> str:
    """Create the folder 'Zeltlagerfilm xxxx' with all its Subfolders"""
    validate_setup_path(path=inputs.folder)
    progress_callback.emit("Input validiert.")
    setup_methods.create_folder_structure(parent=inputs.folder, date=inputs.date)
    return "Ordnerstruktur erfolgreich erstellt."


# ### RAW ### #
def raw_process(titel):
    def decor(func):
        def wrap(*args, **kwargs):
            progress_callback = kwargs["progress_callback"]

            if not is_valid_folder(kwargs["inputs"].raw_material_folder):
                raise ValueError("Bitte gib einen gültigen Rohmaterial ordner an.")
            progress_callback.emit("Inputs validiert")

            result = func(*args, **kwargs)
            _pretty_send_problems(titel=titel, list_=result, progress_callback=progress_callback)
            return f"{titel} abgeschlossen."

        return wrap

    return decor


@raw_process("Korrekte Ordnerstruktur")
def run_correct_structure(inputs: RawTabInput, **kwargs) -> List[str]:
    return raw_methods.correct_file_structure(raw_material_folder=inputs.raw_material_folder,
                                              dst_folder=inputs.raw_material_folder.parent / "New",
                                              start=inputs.first_folder_date)


@raw_process("Dateien umbenennen")
def run_rename_files(inputs: RawTabInput, **kwargs) -> List[str]:
    return raw_methods.run_rename(raw_material_folder=inputs.raw_material_folder)


def run_create_excel(inputs: RawTabInput, progress_callback, get_data, **kwargs) -> Path | None:
    if inputs.excel.option != ExcelOption.CREATE:
        raise AttributeError("Can't call create Excel for existing Excel.")

    if not is_valid_folder(inputs.excel.folder):
        raise AttributeError("The given folder is not a valid folder.")

    progress_callback.emit("Starte Excel erstellen.")
    config = _get_excel_config()
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


def _get_excel_config(excel: ExcelInput) -> ExcelConfig:
    """
    Turn the given configuration for the Excel file to be created into the needed form
    :param excel: user input concerning the Excel file
    :return: Configuration
    """
    vid = constants.minimal_columns.copy()
    vid.extend(excel.video_columns)
    pic = constants.minimal_columns.copy()
    pic.extend(excel.picture_columns)
    return ExcelConfig(
        excel_folder=excel.folder,
        excel_file_name=excel.name,
        sheets=[SheetConfig(name="Videos", columns=vid),
                SheetConfig(name="Bilder", columns=pic)]
    )


@raw_process("Dateien in Excel schreiben")
def run_fill_excel(inputs: RawTabInput, progress_callback, get_data, **kwargs) -> List[str]:
    if inputs.excel.option == ExcelOption.CREATE:
        run_create_excel(inputs, progress_callback, get_data)

    errors = validate_excel_file(inputs.excel.full_path)
    if errors:
        errors.insert(0, "Dateien in Excel schreiben.")
        raise ValueError('\n'.join(errors))
    return raw_methods.fill_excel(excel=inputs.excel.full_path, raw_material_folder=inputs.raw_material_folder)


@raw_process("Bilderordner erstellen")
def run_create_picture_folder(inputs: RawTabInput, **kwargs) -> List[str]:
    inputs.picture_folder.mkdir()
    if not is_valid_folder(inputs.picture_folder):
        raise ValueError("Bitte gib einen gültigen Zielordner an.")

    return raw_methods.create_picture_folder(picture_folder=inputs.picture_folder,
                                             raw_material_folder=inputs.raw_material_folder)


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
                _pretty_send_problems(titel=f"{key} erstellen.", list_=[str(e)], progress_callback=progress_callback)
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
    return util_methods.prepare_dataframes(excel_file=excel_full_filepath,
                                           raw_path=raw_material_folder)


@util_process()
def run_copy_sections(sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback) -> str:
    for sheet_name, do_section in [("Videos", inputs.do_video_sections),
                                   ("Bilder", inputs.do_picture_sections)]:
        if do_section and not sheets[sheet_name].empty:
            results = util_methods.copy_section(df=sheets[sheet_name], rating_limit=inputs.rating_section)
            _pretty_send_problems(titel=f"{sheet_name}abschnitte erstellt.",
                                  list_=results, progress_callback=progress_callback)
    return "Abschnitte abgeschlossen."


@util_process()
def run_copy_selection(sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback) -> str:
    for sheet_name, columns in [("Videos", inputs.videos_columns_selection),
                                ("Bilder", inputs.picture_columns_selection)]:
        if columns and not sheets[sheet_name].empty:
            result = util_methods.copy_selections(df=sheets[sheet_name], raw_path=inputs.raw_material_folder,
                                                  columns=columns, marker=inputs.marker)
            _pretty_send_problems(titel=f"{sheet_name}selektion erstellt.",
                                  list_=result, progress_callback=progress_callback)
    return "Selektionen abgeschlossen."


@util_process()
def run_search(sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback) -> str:
    for sheet_name, columns in [("Videos", inputs.videos_columns_search),
                                ("Bilder", inputs.picture_columns_search)]:
        if columns and not sheets[sheet_name].empty:
            result = util_methods.search_columns(df=sheets[sheet_name], columns=columns,
                                                 raw_path=inputs.raw_material_folder,
                                                 markers=inputs.keywords, rating=inputs.rating_search)
            _pretty_send_problems(titel=f"{sheet_name}suche erstellt.",
                                  list_=result, progress_callback=progress_callback)
    return "Suche abgeschlossen."


@util_process()
def run_create_rated_picture_folder(sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback) -> str:
    result = util_methods.copy_pictures_with_rating(df=sheets["Bilder"],
                                                    raw_path=inputs.raw_material_folder,
                                                    rating_limit=inputs.rating_pictures)
    _pretty_send_problems(titel="Bilderordner", list_=result, progress_callback=progress_callback)
    return "Bilderordner erstellt."


def run_statistics(inputs: UtilTabInput, progress_callback, get_data) -> str:
    progress_callback.emit("Inputs validiert.")
    util_methods.create_statistics(raw_path=inputs.raw_material_folder, progress_callback=progress_callback)
    return "Statistik fertig."


def run_process_util_full(inputs: UtilTabInput, progress_callback, get_data):
    mapping = {
        "Abschnitte": [inputs.do_sections, run_copy_sections],
        "Selektionen": [inputs.do_selections, run_copy_selection],
        "Suche": [inputs.do_search, run_search],
        "Bilderordner": [inputs.create_picture_folder, run_create_rated_picture_folder]
    }
    for key, value in mapping.items():
        if value[0]:
            try:
                # !!! signature of util_process
                progress_callback.emit(
                    value[1](inputs=inputs, progress_callback=progress_callback, get_data=get_data))
            except Exception as e:
                _pretty_send_problems(titel=f"{key} erstellen.", list_=[str(e)], progress_callback=progress_callback)
    return "Prozessierung abgeschlossen"


# Todo duplicate with Worker send_result_list
# use errors Signal
def _pretty_send_problems(list_: List[str], progress_callback, titel=""):
    progress_callback.emit(titel)
    if list_:
        progress_callback.emit("Probleme:")
    [progress_callback.emit(f"- {x}") for x in list_ if x]
