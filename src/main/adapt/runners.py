import time
from pandas import DataFrame
from pathlib import Path
from typing import Dict, List

from assethandling.basemodels import UtilTabInput
from inputhandling.validation import validate_util_paths
from util import util_methods as eval_


def pretty_send_list(list_: List[str], progress_callback):
    if list_:
        progress_callback.emit("Probleme:")
    [progress_callback.emit(f"- {x}") for x in list_ if x]


def execute_function(progress_callback):
    for n in range(0, 5):
        time.sleep(10)
        progress_callback.emit(str(n * 100 / 4))

    return "Done."


def run_copy_sections(inputs: UtilTabInput, progress_callback):
    run_util_processes(handle_sections, inputs, progress_callback)


def run_copy_selection(inputs: UtilTabInput, progress_callback):
    run_util_processes(handle_selection, inputs, progress_callback)


def run_util_processes(function, inputs, progress_callback):
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


def handle_sections(sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback):
    _sections_per_sheet(df=sheets["Videos"],
                        do_sections=inputs.do_video_sections,
                        rating=inputs.rating_section,
                        part="Videos",
                        progress_callback=progress_callback)
    _sections_per_sheet(df=sheets["Bilder"],
                        do_sections=inputs.do_picture_sections,
                        rating=inputs.rating_section,
                        part="Bilder",
                        progress_callback=progress_callback)
    return "Abschnitte abgeschlossen."


def _sections_per_sheet(df: DataFrame, do_sections: bool, rating: int, part: str, progress_callback):
    if do_sections and not df.empty:
        results = eval_.copy_section(df=df, rating_limit=rating)
        progress_callback.emit(f"{part}abschnitte erstellt.")
        pretty_send_list(list_=results, progress_callback=progress_callback)
        return results


def handle_selection(sheets: Dict[str, DataFrame], inputs: UtilTabInput, progress_callback):
    _selection_per_sheet(df=sheets["Videos"],
                         columns=inputs.videos_columns_selection,
                         raw_path=inputs.raw_material_folder,
                         marker=inputs.marker,
                         part="Videos",
                         progress_callback=progress_callback)
    _selection_per_sheet(df=sheets["Bilder"],
                         columns=inputs.picture_columns_selection,
                         raw_path=inputs.raw_material_folder,
                         marker=inputs.marker,
                         part="Bilder",
                         progress_callback=progress_callback)
    return "Selektionen abgeschlossen."


def _selection_per_sheet(df: DataFrame, columns: List[str],
                         raw_path: Path, marker: str, part: str,
                         progress_callback):
    if columns and not df.empty:
        result = eval_.copy_selections(df=df,
                                       raw_path=raw_path,
                                       columns=columns,
                                       marker=marker)
        progress_callback.emit(f"{part}abschnitte erstellt.")
        pretty_send_list(list_=result, progress_callback=progress_callback)
