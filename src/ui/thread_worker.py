from pathlib import Path
from typing import List, Dict

import pandas as pd
from PyQt5.QtCore import *

from assethandling.asset_manager import settings
from inputhandling import validation
from foldersetup import folder_structure
from excel.excelmethods import create_emtpy_excel
from assethandling.basemodels import ExcelOptions, SheetConfig, FolderTabInput, UtilTabInput
from stats import statistics
from util import util_methods as eval


class Worker(QThread):
    problem_with_input = pyqtSignal(str)
    process_finished = pyqtSignal(str)

    new_message_setup = pyqtSignal(str)

    new_message_raw = pyqtSignal(str)
    excel_exits_error = pyqtSignal()

    new_message_excel = pyqtSignal(str)

    @pyqtSlot(str, QDate)
    def setup_folder_structure(self, inputs: FolderTabInput):
        """Create the folder 'Zeltlagerfilm xxxx with all its Subfolders"""
        valid, error = validation.validate_setup_path(path=inputs.folder)
        if valid:
            self.new_message_setup.emit("Input validiert.")
            folder_structure.create_folder_structure(parent=inputs.folder, date=inputs.date)
            self.new_message_setup.emit("Ordner erfolgreich erstellt.")
        else:
            self.problem_with_input.emit(error)
        self.process_finished.emit("Ordnerstruktur erfolgreich erstellt")

    # ### RAW
    @pyqtSlot(Path)
    def correct_file_structure(self, path: Path):
        # check if in correct order?
        # take all file, sort by date
        # for every day in create folder with Bilder und Videos
        # take Date for LKW einladen -> everything else in Sonstiges
        pass

    @pyqtSlot(Path)
    def rename_files(self, path: Path):
        # Validation
        # Format as so far
        # enumeration per folder
        pass

    @pyqtSlot()
    def create_excel(self, file_name: str,
                     path: Path,
                     option=ExcelOptions.STANDARD,
                     columns=None,
                     override=False):
        try:
            if file_name is None or not isinstance(path, Path) or not path.exists():
                raise AttributeError("Incorrect Input.")
            self.new_message_raw.emit("Starte Excel erstellen.")
            if option == ExcelOptions.STANDARD:
                sheets: List[SheetConfig] = [SheetConfig(name="Videos", columns=settings["standard-video-columns"]),
                                             SheetConfig(name="Bilder", columns=settings["standard-picture-columns"])]
            elif option == ExcelOptions.MANUAL and columns is not None:
                sheets: List[SheetConfig] = [SheetConfig(name="Videos", columns=columns[0]),
                                             SheetConfig(name="Bilder", columns=columns[1])]
            else:
                self.problem_with_input.emit("Called Function with incorrect parameters. \n"
                                             "Don't call with EXISTING or forget columns for manual.")
                return
            create_emtpy_excel(file_name=file_name, path=path, sheets=sheets, override=override)
            self.new_message_raw.emit("Excel-Datei erfolgreich erstellt")
        except FileExistsError:
            self.excel_exits_error.emit()
        except Exception as e:
            print(e)
            self.problem_with_input.emit(str(e))

    @pyqtSlot()
    def fill_excel(self):
        pass

    @pyqtSlot()
    def create_picture_folder(self):
        pass

    # ### UTIL ### #
    @staticmethod
    def _validate_and_prepare(raw_material_folder: Path, excel_full_filepath: Path) -> Dict[str, pd.DataFrame]:
        valid, errors = validation.validate_util_paths(raw_material_folder=raw_material_folder,
                                                       excel_full_filepath=excel_full_filepath)
        if not valid:
            raise ValueError('\n'.join(errors))
        return eval.prepare_dataframes(excel_file=excel_full_filepath,
                                       raw_path=raw_material_folder)

    @pyqtSlot(UtilTabInput)
    def full_util_tab(self, inputs: UtilTabInput):
        try:
            sheets = self._validate_and_prepare(raw_material_folder=inputs.raw_material_folder,
                                                excel_full_filepath=inputs.excel_full_filepath)
        except Exception as e:
            self.problem_with_input.emit(str(e))
            return
        self.new_message_excel.emit("Inputs validiert und Excel eingelesen.")

        if inputs.do_sections:
            try:
                self._handle_section(sheets=sheets, inputs=inputs)
            except Exception as e:
                self.problem_with_input.emit(str(e))
        if inputs.do_selections:
            try:
                self._handle_selection(sheets=sheets, inputs=inputs)
            except Exception as e:
                self.problem_with_input.emit(str(e))
        if inputs.do_search:
            try:
                self._handle_search(sheets=sheets, inputs=inputs)
            except Exception as e:
                self.problem_with_input.emit(str(e))
        if inputs.create_picture_folder:
            try:
                self._handle_picture_folder(sheets=sheets, inputs=inputs)
            except Exception as e:
                self.problem_with_input.emit(str(e))

        self.process_finished.emit("BlaBla: util gesamt fertig")

    @pyqtSlot(UtilTabInput)
    def run_copy_sections(self, inputs: UtilTabInput):
        try:
            sheets = self._validate_and_prepare(raw_material_folder=inputs.raw_material_folder,
                                                excel_full_filepath=inputs.excel_full_filepath)
        except Exception as e:
            self.problem_with_input.emit(str(e))
            return
        self.new_message_excel.emit("Inputs validiert und Excel eingelesen.")
        self._handle_section(sheets=sheets, inputs=inputs)

    def _handle_section(self, sheets: Dict[str, pd.DataFrame], inputs: UtilTabInput):
        self._section_per_sheet(df=sheets["Videos"],
                                do_sections=inputs.do_video_sections,
                                rating=inputs.rating_section,
                                part="Videos")
        self._section_per_sheet(df=sheets["Bilder"],
                                do_sections=inputs.do_picture_sections,
                                rating=inputs.rating_section,
                                part="Bilder")

    def _section_per_sheet(self, df: pd.DataFrame, do_sections: bool, rating: int, part: str):
        if do_sections and not df.empty:
            result = eval.copy_section(df=df, rating_limit=rating)
            self._send_results(part=f"{part}abschnitte erstellt.", result=result)

    @pyqtSlot(UtilTabInput)
    def run_selection(self, inputs: UtilTabInput):
        try:
            sheets = self._validate_and_prepare(raw_material_folder=inputs.raw_material_folder,
                                                excel_full_filepath=inputs.excel_full_filepath)
        except Exception as e:
            self.problem_with_input.emit(str(e))
            return
        self.new_message_excel.emit("Inputs validiert und Excel eingelesen.")
        self._handle_selection(sheets=sheets, inputs=inputs)

    def _handle_selection(self, sheets: Dict[str, pd.DataFrame], inputs: UtilTabInput):
        self._selection_per_sheet(df=sheets["Videos"],
                                  columns=inputs.videos_columns_selection,
                                  raw_path=inputs.raw_material_folder,
                                  marker=inputs.marker,
                                  part="Videos")
        self._selection_per_sheet(df=sheets["Bilder"],
                                  columns=inputs.picture_columns_selection,
                                  raw_path=inputs.raw_material_folder,
                                  marker=inputs.marker,
                                  part="Bilder")

    def _selection_per_sheet(self, df: pd.DataFrame, columns: List[str],
                             raw_path: Path, marker: str, part: str):
        if columns and not df.empty:
            result = eval.copy_selections(df=df,
                                          raw_path=raw_path,
                                          columns=columns,
                                          marker=marker)
            self._send_results(part=f"{part}selektionen erstellt.", result=result)

    @pyqtSlot(UtilTabInput)
    def run_search(self, inputs: UtilTabInput):
        try:
            sheets = self._validate_and_prepare(raw_material_folder=inputs.raw_material_folder,
                                                excel_full_filepath=inputs.excel_full_filepath)
        except Exception as e:
            self.problem_with_input.emit(str(e))
            return
        self.new_message_excel.emit("Inputs validiert und Excel eingelesen.")
        self._handle_search(sheets=sheets, inputs=inputs)

    def _handle_search(self, sheets: Dict[str, pd.DataFrame], inputs: UtilTabInput):
        self._search_per_sheet(df=sheets["Videos"],
                               columns=inputs.videos_columns_search,
                               raw_path=inputs.raw_material_folder,
                               keywords=inputs.keywords,
                               rating=inputs.rating_search,
                               part="Videos")
        self._search_per_sheet(df=sheets["Bilder"],
                               columns=inputs.picture_columns_search,
                               raw_path=inputs.raw_material_folder,
                               keywords=inputs.keywords,
                               rating=inputs.rating_search,
                               part="Bilder")

    def _search_per_sheet(self, df: pd.DataFrame, columns: List[str], raw_path: Path,
                          keywords: List[str], rating: int, part: str):
        if columns and not df.empty:
            result = eval.search_columns(df=df,
                                         raw_path=raw_path,
                                         columns=columns,
                                         markers=keywords,
                                         rating=rating)
            self._send_results(part=f"{part}suche erstellt.", result=result)

    @pyqtSlot(UtilTabInput)
    def run_copy_picture_folder(self, inputs):
        try:
            sheets = self._validate_and_prepare(raw_material_folder=inputs.raw_material_folder,
                                                excel_full_filepath=inputs.excel_full_filepath)
        except Exception as e:
            self.problem_with_input.emit(str(e))
            return
        self.new_message_excel.emit("Inputs validiert und Excel eingelesen.")
        self._handle_picture_folder(sheets=sheets, inputs=inputs)

    def _handle_picture_folder(self, sheets: Dict[str, pd.DataFrame], inputs: UtilTabInput):
        result = eval.copy_pictures_with_rating(df=sheets["Bilder"],
                                                raw_path=inputs.raw_material_folder,
                                                rating_limit=inputs.rating_pictures)
        self._send_results(part="Bilderordner erstellt.", result=result)

    @pyqtSlot(Path)
    def run_statistics(self, raw_path):
        self.new_message_excel.emit("Inputs validiert und Excel eingelesen.")
        try:
            select = raw_path.parent / "Schnittmaterial"
            total_duration, problems, duration_per_day = statistics.get_raw_material_duration(path=raw_path)

            result = [f"Gesamtdauer: {total_duration}"]
            for day in duration_per_day:
                result.append(f"Dauer am Tag {day[0]} ist {day[1]}.")
            result.append(statistics.percent_selected(raw=raw_path, selected=select))

            self.new_message_excel.emit('\n'.join(result))

            # with open(select / "statistics.txt", 'w') as outfile:
                # outfile.write('\n'.join(result))

        except Exception as e:
            self.problem_with_input.emit(str(e))
            return

    def _send_results(self, part: str, result: List[str]):
        self.new_message_excel.emit(part)
        if result:
            self.new_message_excel.emit("Probleme:")
        [self.new_message_excel.emit(f"- {x}") for x in result if x]