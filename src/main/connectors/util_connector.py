import time
from pandas import DataFrame
from pathlib import Path
from typing import Dict, List

from assethandling.basemodels import UtilTabInput

from util import util_methods as eval_
from util.stats import statistics


# Todo duplicate with Worker send_result_list
def pretty_send_list(list_: List[str], progress_callback, titel=""):
    progress_callback.emit(titel)
    if list_:
        progress_callback.emit("Probleme:")
    [progress_callback.emit(f"- {x}") for x in list_ if x]


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