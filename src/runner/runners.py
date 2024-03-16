from pathlib import Path
from typing import Dict, List

from pandas import DataFrame

from assethandling import constants
from assethandling.basemodels import (ExcelConfig, ExcelInput, ExcelOption,
                                      FolderTabInput, RawTabInput, SheetConfig,
                                      UtilTabInput)
from foldersetup import folder_setup as setup_methods
from inputhandling.validation import (is_valid_folder, validate_excel_file,
                                      validate_raw, validate_setup_path,
                                      validate_util_paths)
from rawmaterial import raw_material as raw_methods
from util import util_methods as util_methods


# ### SETUP ### #
def run_folder_setup(inputs: FolderTabInput, progress_callback, get_data) -> str:
    """Create the folder 'Zeltlagerfilm xxxx' with all its Subfolders"""
    validate_setup_path(path=inputs.folder)
    progress_callback.emit("Input validiert.")
    setup_methods.create_folder_structure(parent=inputs.folder, date=inputs.date)
    return "Ordnerstruktur erfolgreich erstellt."


# ### RAW ### #
def raw_process():
    def decor(func):
        def wrap(
            inputs: RawTabInput, progress_callback, get_data, *args, **kwargs
        ) -> str:
            if not is_valid_folder(inputs.raw_material_folder):
                raise ValueError("Bitte gib einen gültigen Rohmaterialordner an.")
            progress_callback.emit("Inputs validiert")

            msg: str = func(
                inputs=inputs, progress_callback=progress_callback, get_data=get_data
            )
            return msg

        return wrap

    return decor


@raw_process()
def run_correct_structure(
    inputs: RawTabInput, progress_callback, get_data, **kwargs
) -> str:
    raw_methods.correct_file_structure(
        raw_material_folder=inputs.raw_material_folder,
        dst_folder=inputs.raw_material_folder.parent / "New",
        start=inputs.first_folder_date,
        progress_callback=progress_callback,
        get_data=get_data,
    )
    return "Korrekte Ordnerstruktur abgeschlossen"


@raw_process()
def run_rename_files(inputs: RawTabInput, progress_callback, **kwargs) -> str:
    raw_methods.run_rename(
        raw_material_folder=inputs.raw_material_folder,
        progress_callback=progress_callback,
    )
    return "Dateien umbenennen abgeschlossen"


def run_create_excel(inputs: RawTabInput, progress_callback, get_data, **kwargs):
    if inputs.excel.option != ExcelOption.CREATE:
        raise AttributeError("Can't call create Excel for existing Excel.")

    if not is_valid_folder(inputs.excel.folder):
        raise AttributeError("The given folder is not a valid folder.")

    progress_callback.emit("Starte Excel erstellen.")
    config: ExcelConfig = _get_excel_config(excel=inputs.excel)
    raw_methods.create_excel(
        config=config, progress_callback=progress_callback, get_data=get_data
    )


def _get_excel_config(excel: ExcelInput) -> ExcelConfig:
    """
    Turn the given configuration for the Excel file to be created into the needed form
    :param excel: user input concerning the Excel file
    :return: Configuration
    """
    vid: List[str] = constants.minimal_columns.copy()
    vid.extend(excel.video_columns)
    pic: List[str] = constants.minimal_columns.copy()
    pic.extend(excel.picture_columns)
    return ExcelConfig(
        excel_folder=excel.folder,
        excel_file_name=excel.name,
        sheets=[
            SheetConfig(name="Videos", columns=vid),
            SheetConfig(name="Bilder", columns=pic),
        ],
    )


@raw_process()
def run_fill_excel(inputs: RawTabInput, progress_callback, get_data, **kwargs) -> str:
    if inputs.excel.option == ExcelOption.CREATE:
        run_create_excel(inputs, progress_callback, get_data)

    errors = validate_excel_file(inputs.excel.full_path)
    if errors:
        errors.insert(0, "Dateien in Excel schreiben.")
        raise ValueError("\n".join(errors))
    raw_methods.fill_excel(
        excel=inputs.excel.full_path,
        raw_material_folder=inputs.raw_material_folder,
        progress_callback=progress_callback,
    )
    return "Dateien in Excel schreiben abgeschlossen"


@raw_process()
def run_create_picture_folder(inputs: RawTabInput, progress_callback, **kwargs) -> str:
    inputs.picture_folder.mkdir()
    if not is_valid_folder(inputs.picture_folder):
        raise ValueError("Bitte gib einen gültigen Zielordner an.")

    raw_methods.create_picture_folder(
        picture_folder=inputs.picture_folder,
        raw_material_folder=inputs.raw_material_folder,
        progress_callback=progress_callback,
    )
    return "Bilderordner erstellen abgeschlossen"


def run_process_raw_full(inputs: RawTabInput, progress_callback, get_data) -> str:
    validate_raw(inputs)
    mapping = {
        "Korrekte Ordnerstruktur": [inputs.do_structure, run_correct_structure],
        "Umbenennen": [inputs.do_rename, run_rename_files],
        "Dateien in Excel schreiben": [inputs.fill_excel, run_fill_excel],
        "Bilderordner erstellen": [
            inputs.create_picture_folder,
            run_create_picture_folder,
        ],
    }
    for key, value in mapping.items():
        if value[0]:
            try:
                msg: str = value[1](
                    inputs=inputs,
                    progress_callback=progress_callback,
                    get_data=get_data,
                )
                progress_callback.emit(msg)
            except Exception as e:
                progress_callback.emit(
                    f"! Problem beim {key} erstellen:\n" f"- Fehler: {str(e)}"
                )
    return "Gesammelt ausführen abgeschlossen."


# ### UTIL ### #
def util_process():
    def decor(func):
        def wrap(inputs: UtilTabInput, progress_callback, get_data, *args, **kwargs):
            sheets = validate_and_prepare(
                raw_material_folder=inputs.raw_material_folder,
                excel_full_filepath=inputs.excel_full_filepath,
            )
            progress_callback.emit("Inputs validiert und Excel eingelesen.")

            msg = func(
                sheets=sheets, inputs=inputs, progress_callback=progress_callback
            )
            return msg

        return wrap

    return decor


def validate_and_prepare(
    raw_material_folder: Path, excel_full_filepath: Path
) -> Dict[str, DataFrame]:
    validate_util_paths(
        raw_material_folder=raw_material_folder, excel_full_filepath=excel_full_filepath
    )
    return util_methods.prepare_dataframes(
        excel_file=excel_full_filepath, raw_path=raw_material_folder
    )


@util_process()
def run_copy_sections(
    sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback
) -> str:
    for sheet_name, do_section in [
        ("Videos", inputs.do_video_sections),
        ("Bilder", inputs.do_picture_sections),
    ]:
        if do_section and not sheets[sheet_name].empty:
            util_methods.copy_section(
                df=sheets[sheet_name],
                rating_limit=inputs.rating_section,
                progress_callback=progress_callback,
            )
            progress_callback.emit(f"{sheet_name}abschnitte erstellt.")
    return "Abschnitte abgeschlossen."


@util_process()
def run_copy_selection(
    sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback
) -> str:
    for sheet_name, columns in [
        ("Videos", inputs.videos_columns_selection),
        ("Bilder", inputs.picture_columns_selection),
    ]:
        if columns and not sheets[sheet_name].empty:
            util_methods.copy_selections(
                df=sheets[sheet_name],
                raw_path=inputs.raw_material_folder,
                columns=columns,
                marker=inputs.marker,
                progress_callback=progress_callback,
            )
            progress_callback.emit(f"{sheet_name}selektion erstellt.")
    return "Selektionen abgeschlossen."


@util_process()
def run_search(
    sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback
) -> str:
    for sheet_name, columns in [
        ("Videos", inputs.videos_columns_search),
        ("Bilder", inputs.picture_columns_search),
    ]:
        if columns and not sheets[sheet_name].empty:
            util_methods.search_columns(
                df=sheets[sheet_name],
                columns=columns,
                raw_path=inputs.raw_material_folder,
                markers=inputs.keywords,
                rating=inputs.rating_search,
                progress_callback=progress_callback,
            )
            progress_callback.emit(f"{sheet_name}suche erstellt.")
    return "Suche abgeschlossen."


@util_process()
def run_create_rated_picture_folder(
    sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback
) -> str:
    util_methods.copy_pictures_with_rating(
        df=sheets["Bilder"],
        raw_path=inputs.raw_material_folder,
        rating_limit=inputs.rating_pictures,
        progress_callback=progress_callback,
    )
    return "Bilderordner erstellt."


def run_statistics(inputs: UtilTabInput, progress_callback, get_data) -> str:
    progress_callback.emit("Inputs validiert.")
    util_methods.create_statistics(
        raw_path=inputs.raw_material_folder, progress_callback=progress_callback
    )
    return "Statistik fertig."


def run_process_util_full(inputs: UtilTabInput, progress_callback, get_data):
    mapping = {
        "Abschnitte": [inputs.do_sections, run_copy_sections],
        "Selektionen": [inputs.do_selections, run_copy_selection],
        "Suche": [inputs.do_search, run_search],
        "Bilderordner": [inputs.create_picture_folder, run_create_rated_picture_folder],
    }
    for key, value in mapping.items():
        if value[0]:
            try:
                # !!! signature of util_process
                progress_callback.emit(
                    value[1](
                        inputs=inputs,
                        progress_callback=progress_callback,
                        get_data=get_data,
                    )
                )
            except Exception as e:
                progress_callback.emit(
                    f"! Problem beim {key} erstellen:\n" f"- Fehler: {str(e)}"
                )
    return "Prozessierung abgeschlossen"
