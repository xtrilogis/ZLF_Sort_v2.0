import locale
from pathlib import Path
from typing import Dict, List
from datetime import datetime

import pandas as pd
from pydantic import ValidationError

from assethandling import constants
from assethandling.basemodels import ExcelConfig, File, FileType, RenameType
from excel.excelmethods import (
    create_emtpy_excel,
    load_sheets_as_df,
    save_sheets_to_excel,
)
from fileopertations.filemethods import (
    copy_file,
    get_file_captured_date,
    get_file_type,
    rename_files,
)

locale.setlocale(locale.LC_TIME, "de_DE.utf8")


def _add_file_object(file: Path, rename_type: RenameType, all_files: List[File], progress_callback):
    if not file.is_file():
        return

    file_type = get_file_type(file)
    if file_type != FileType.IMAGE and file_type != FileType.VIDEO:
        return

    datum: datetime = get_file_captured_date(file, file_type)
    if rename_type.FOLDER:
        try:
            try:
                zlf_folder: str = file.parent.parent.parent.parent.name
                year: int = int(zlf_folder.split(" ")[1])
            except Exception:
                year: int = datetime.now().year

            folder_name: str = file.parent.parent.name
            date_part: str = folder_name.split('-')[1]
            folder_date: datetime = datetime.strptime(date_part, "%d.%m")

            datum: datetime = datetime(year, folder_date.month, folder_date.day,
                             datum.hour, datum.minute, datum.second)
        except Exception:
            pass
    try:
        all_files.append(
            File(full_path=file, date=datum, dst_folder=None, type=file_type)
        )
    except ValidationError as e:
        progress_callback.emit(f"Fehler: Datei {file.name} \n {str(e)}")


def run_rename(raw_material_folder: Path, rename_type: RenameType, progress_callback):
    _rename_files_in_folder(
        folder=raw_material_folder, rename_type=rename_type, progress_callback=progress_callback
    )

    for element in raw_material_folder.glob("**/*"):
        _rename_files_in_folder(folder=element, rename_type=rename_type, progress_callback=progress_callback)


def _rename_files_in_folder(folder: Path, rename_type: RenameType, progress_callback):
    if _is_folder_with_material(folder):
        all_files: List[File] = []
        for child in folder.iterdir():
            _add_file_object(
                file=child, all_files=all_files, rename_type=rename_type, progress_callback=progress_callback
            )
        all_files.sort(key=lambda x: x.date, reverse=False)

        rename_files(
            folder=folder, all_files=all_files, progress_callback=progress_callback
        )


def _is_folder_with_material(path: Path) -> bool:
    if not path.is_dir():
        return False
    for element in path.iterdir():
        if (
            element.suffix.upper() in constants.video_extensions
            or element.suffix.upper() in constants.image_extensions
        ):
            return True
    return False


def create_excel(config: ExcelConfig, progress_callback, get_data):
    try:
        path = create_emtpy_excel(config=config)
        progress_callback.emit("Excel-Datei erfolgreich erstellt.")
        return path
    except FileExistsError:
        response: str = get_data(
            text="Excel existiert bereits. Soll sie überschrieben werden? Ja/Nein"
        )
        if response == "Ja":
            progress_callback.emit("Excel-Datei wird überschrieben.")
            path = create_emtpy_excel(config=config, override=True)
            progress_callback.emit("Excel-Datei erfolgreich erstellt.")
            return path
        progress_callback.emit(
            "Excel wurde nicht erstellt, da die Datei bereits vorhanden ist."
        )


def fill_excel(excel: Path, raw_material_folder: Path, progress_callback):
    sheets: Dict[str, pd.DataFrame] = load_sheets_as_df(excel)
    if not sheets["Videos"].empty or not sheets["Bilder"].empty:
        # feat: ask if Excel should be overwritten
        raise ValueError("Die Excel enthält bereits Daten.")

    for element in raw_material_folder.glob("**/*"):
        if _is_folder_with_material(element):
            _fill_sheets(
                folder=element, sheets=sheets, progress_callback=progress_callback
            )

    save_sheets_to_excel(sheets=sheets, path=excel)


def _fill_sheets(folder: Path, sheets: Dict[str, pd.DataFrame], progress_callback):
    picture_folder_written = False
    video_folder_written = False
    for element in folder.iterdir():
        try:
            if element.suffix.upper() in constants.video_extensions:
                if not video_folder_written:
                    sheets["Videos"].loc[
                        len(sheets["Videos"]), "Datei"
                    ] = folder.parent.name
                    video_folder_written = True
                sheets["Videos"].loc[len(sheets["Videos"]), "Datei"] = element.name

            if element.suffix.upper() in constants.image_extensions:
                if not picture_folder_written:
                    sheets["Bilder"].loc[
                        len(sheets["Bilder"]), "Datei"
                    ] = folder.parent.name
                    picture_folder_written = True
                sheets["Bilder"].loc[len(sheets["Bilder"]), "Datei"] = element.name
        except IndexError as e:
            progress_callback.emit(
                f"Fehler: Datei {element.name} nicht in der Excel-Datei gefunden."
            )


def create_picture_folder(
    picture_folder: Path, raw_material_folder: Path, progress_callback
):
    # feat: check if folder contains elements and then ask for handling
    for element in raw_material_folder.glob("**/*"):
        if element.suffix.upper() in constants.image_extensions:
            try:
                copy_file(element, picture_folder)
            except (FileNotFoundError, FileExistsError) as e:
                progress_callback.emit(
                    f"Datei {element.name} wurde nicht umbenannt\n"
                    f"- Fehler: {type(e).__name__}"
                )
