from pathlib import Path
from typing import Dict, List

import pandas as pd

from assethandling import constants
from excel import excelmethods
from fileopertations import filemethods
from util.stats import statistics


def prepare_dataframes(excel_file: Path, raw_path: Path) -> Dict[str, pd.DataFrame]:
    sheets = excelmethods.load_sheets_as_df(path=excel_file)
    if sheets["Videos"].empty and sheets["Bilder"].empty:
        raise ValueError("Die Excel enthält keine Daten. Bitte ausfüllen.")
    _append_file_paths_to_df(sheets=sheets, raw_material_path=raw_path)
    return sheets


def _append_file_paths_to_df(sheets: Dict[str, pd.DataFrame], raw_material_path: Path):
    """Creates a new column 'Dateipfad' and fills it with the files fullpath
    :arg sheets pandas DataFrames with the all files and the markers
    :arg raw_material_path
    :returns df with new filled column 'Dateipfad' (eng. 'filepath')"""
    sheets["Videos"]["Dateipfad"] = pd.Series(dtype="str")
    sheets["Bilder"]["Dateipfad"] = pd.Series(dtype="str")
    for element in raw_material_path.glob("**/*"):
        if element.is_file():
            if element.suffix.upper() in constants.video_extensions:
                df = sheets["Videos"]
            elif element.suffix.upper() in constants.image_extensions:
                df = sheets["Bilder"]
            else:
                continue

            match = df.loc[df["Datei"] == element.name]
            if not match.empty:
                row = match.index[0]
                df.loc[row, "Dateipfad"] = element


def copy_section(df: pd.DataFrame, rating_limit: int, progress_callback):
    """Iterates through column 'Abschnitt'(Sections), sorts files into given sections
    :param progress_callback: _
    :arg df pandas DataFrame containing file information
    :arg rating_limit only file with a rating equal or higher will be copied"""
    copied_files_nr: int = 0
    for count, value in enumerate(df["Abschnitt"]):
        rating = df.loc[count, "Bewertung"]
        if pd.isnull(value) and pd.isnull(rating):
            continue
        if pd.isnull(value):
            value = "Sonstiges"
        try:
            if int(rating) >= rating_limit:
                if pd.isnull(df.loc[count, "Dateipfad"]):
                    progress_callback.emit(
                        f"Datei konnte nicht kopiert werden: {df.loc[count, 'Datei']}"
                    )
                    continue

                file_fullpath = Path(df.loc[count, "Dateipfad"])
                section = value.strip()
                destination_folder = _get_section_dst_folder(
                    file_fullpath=file_fullpath, section=section
                )
                filemethods.copy_file(
                    src_file=file_fullpath, dst_folder=destination_folder
                )
                copied_files_nr += 1
        except (AttributeError, ValueError) as e:
            progress_callback.emit(str(e))
        except FileNotFoundError as e:
            progress_callback.emit(f"Datei nicht gefunden: {df.loc[count, 'Datei']}")
    progress_callback.emit(f"{copied_files_nr} Dateien kopiert.")


def _get_section_dst_folder(file_fullpath: Path, section: str) -> Path:
    new_parts = []
    for _, part in enumerate(file_fullpath.parent.parts):
        if part == "Rohmaterial":
            part = "Schnittmaterial"
        new_parts.append(part)
    destination = Path(*new_parts) / section
    if not destination.exists():
        destination.mkdir(parents=True)
    return destination


def copy_selections(
    df: pd.DataFrame, raw_path: Path, columns: List[str], marker: str, progress_callback
):
    problems = []
    dst_folder = raw_path.parent / "Schnittmaterial" / "Selektionen"
    for column in columns:
        if column in df.columns:
            current_folder = dst_folder / column
            _copy_marked_files(
                df=df,
                column=column,
                marker=marker,
                current_folder=current_folder,
                progress_callback=progress_callback,
            )
        else:
            progress_callback.emit(f"Spalte {column} nicht gefunden.")


def search_columns(
    df: pd.DataFrame,
    raw_path: Path,
    columns: List[str],
    markers: List[str],
    rating: int,
    progress_callback,
):
    dst_folder: Path = raw_path.parent / "Schnittmaterial" / "Suche"
    for marker in markers:
        current_folder: Path = dst_folder / marker
        for column in columns:
            if column in df.columns:
                _copy_marked_files(
                    df=df,
                    column=column,
                    marker=marker,
                    current_folder=current_folder,
                    rating=rating,
                    progress_callback=progress_callback,
                )
            else:
                progress_callback.emit(f"Spalte {column} nicht gefunden.")


def _copy_marked_files(
    df: pd.DataFrame,
    column: str,
    marker: str,
    current_folder: Path,
    progress_callback,
    rating=0,
):
    copied_files_nr: int = 0
    for count, value in enumerate(df[column]):
        if pd.isnull(value):
            pass
        elif marker in value and df.loc[count, "Bewertung"] >= rating:
            if pd.isnull(df.loc[count, "Dateipfad"]):
                progress_callback.emit(
                    f"Datei konnte nicht kopiert werden: {df.loc[count, 'Datei']}"
                )
                continue
            file_fullpath: Path = Path(df.loc[count, "Dateipfad"])

            filemethods.copy_file(src_file=file_fullpath, dst_folder=current_folder)
            copied_files_nr += 1

    progress_callback.emit(
        f"{copied_files_nr} Dateien kopiert. \n für Spalte {column}, Marker: {marker}"
    )


def copy_pictures_with_rating(
    df: pd.DataFrame, raw_path: Path, rating_limit: int, progress_callback
):
    copied_files_nr: int = 0
    dst_folder: Path = raw_path.parent / "Schnittmaterial" / f"Bilder bw{rating_limit}"
    for count, value in enumerate(df["Dateipfad"]):
        if pd.isnull(value):
            if not pd.isnull(df.loc[count, "Bewertung"]):
                progress_callback.emit(
                    f"Datei konnte nicht ausgewertet werden: {df.loc[count, 'Datei']}"
                )
            continue
        if df.loc[count, "Bewertung"] >= rating_limit:
            filemethods.copy_file(src_file=value, dst_folder=dst_folder)
            copied_files_nr += 1
    progress_callback.emit(f"{copied_files_nr} Dateien kopiert.")


def create_statistics(raw_path: Path, progress_callback):
    select: Path = raw_path.parent / "Schnittmaterial"

    total_duration, problems, duration_per_day = statistics.get_raw_material_duration(
        path=raw_path
    )
    result: List[str] = [f"Gesamtdauer: {total_duration}"]
    progress_callback.emit("Gesamtdauer ermittelt.")

    for day in duration_per_day:
        result.append(f"Dauer am Tag {day[0]} ist {day[1]}.")
    progress_callback.emit("Dauer pro Tag ermittelt.")

    result.append(statistics.percent_selected(raw=raw_path, selected=select))
    progress_callback.emit("Verwendeter Anteil ermittelt.")

    progress_callback.emit("\n".join(result))
