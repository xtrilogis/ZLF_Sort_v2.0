from datetime import datetime
from pathlib import Path
from typing import List, Dict

import pandas as pd
from PyQt5.QtCore import *  # TODO better

from inputhandling import validation
from foldersetup import folder_setup
from excel.excelmethods import create_emtpy_excel
from assethandling.basemodels import SheetConfig, FolderTabInput, UtilTabInput, ExcelConfig, ExcelInput, \
    RawTabInput
from stats import statistics
from util import util_methods as eval_
from inputhandling.validation import validate_folder, validate_excel_file
from rawmaterial.raw_material import correct_file_structure, run_rename, fill_excel, create_picture_folder


class Worker(QThread):
    problem_with_input = pyqtSignal(str)
    process_finished = pyqtSignal(str)

    new_message_setup = pyqtSignal(str)

    new_message_raw = pyqtSignal(str)
    excel_exits_error = pyqtSignal()
    excel_exits_in_process_error = pyqtSignal()

    new_message_excel = pyqtSignal(str)
    excel_created = pyqtSignal(Path)

    @pyqtSlot(str, QDate)
    def setup_folder_structure(self, inputs: FolderTabInput):
        """Create the folder 'Zeltlagerfilm xxxx with all its Subfolders"""
        valid, error = validation.validate_setup_path(path=inputs.folder)
        if valid:
            self.new_message_setup.emit("Input validiert.")
            folder_setup.create_folder_structure(parent=inputs.folder, date=inputs.date)
            self.new_message_setup.emit("Ordner erfolgreich erstellt.")
        else:
            self.problem_with_input.emit(error)
        self.process_finished.emit("Ordnerstruktur erfolgreich erstellt")

    # ### RAW
    @pyqtSlot(RawTabInput)
    def run_raw_full(self, inputs: RawTabInput):
        errors = validation.validate_raw(inputs)
        if errors:
            self._send_results_raw("Prozess voll", errors)
            self.problem_with_input.emit("")
            return
        if inputs.do_structure:
            try:
                result = correct_file_structure(
                    raw_material_folder=inputs.raw_material_folder,
                    dst_folder=inputs.raw_material_folder.parent / "New",
                    start=inputs.first_folder_date
                )
                self._send_results_raw(part="Struktur", result=result)
            except Exception as e:
                print(str(e))
        if inputs.do_rename:
            try:
                result = run_rename(raw_material_folder=inputs.raw_material_folder)
                self._send_results_raw(part="Umbenennen", result=result)
            except Exception as e:
                print(str(e))
        if inputs.fill_excel:
            try:
                result = fill_excel(excel=inputs.excel_config.excel_full_filepath,
                                    raw_material_folder=inputs.raw_material_folder)
                self._send_results_raw(part="Excel schreiben", result=result)
            except Exception as e:
                print(str(e))
        if inputs.create_picture_folder:
            try:
                result = create_picture_folder(picture_folder=inputs.picture_folder,
                                               raw_material_folder=inputs.raw_material_folder)
                self._send_results_raw(part="Bilderordner", result=result)
            except Exception as e:
                print(str(e))

        print("BlaBla: raw gesamt fertig")

    @pyqtSlot(Path)
    def run_correct_file_structure(self, path: Path, start: datetime):
        if not validate_folder(path) and not isinstance(start, datetime):
            self.problem_with_input.emit(str("!!!! Fehler !!!"))
            return

        self.new_message_excel.emit("Inputs validiert und Excel eingelesen.")
        result = correct_file_structure(raw_material_folder=path,
                                        dst_folder=path.parent / "New",
                                        start=start)
        self._send_results_raw(part="Korrekte Ordnerstruktur", result=result)
        self.process_finished.emit("Korrekte Ordnerstruktur abgeschlossen.")

    @pyqtSlot(Path)
    def rename_files(self, path: Path):
        if not validate_folder(path):
            self.problem_with_input.emit(str("!!!! Fehler !!!"))
            return

        result = run_rename(raw_material_folder=path)
        self._send_results_raw(part="Dateien umbenennen.", result=result)
        self.process_finished.emit("Umbenennen abgeschlossen.")

    @pyqtSlot(ExcelInput, bool)
    def create_excel_normal(self, input_: ExcelInput, override: bool):
        try:
            self._handle_excel_creation(input_=input_, override=override)
        except FileExistsError:
            self.excel_exits_error.emit()
        except Exception as e:
            self.problem_with_input.emit(str(e))

    @pyqtSlot(ExcelInput, bool)
    def create_excel_in_process(self, input_: ExcelInput, override: bool):
        try:
            path = self._handle_excel_creation(input_=input_, override=override)
            self.excel_created.emit(path)
        except FileExistsError:
            self.excel_exits_in_process_error.emit()
        except Exception as e:
            self.problem_with_input.emit(str(e))

    def _handle_excel_creation(self, input_: ExcelInput, override) -> Path:
        if not validate_folder(input_.excel_folder):
            raise AttributeError("Incorrect Input.")

        self.new_message_raw.emit("Starte Excel erstellen.")
        config = ExcelConfig(
            excel_folder=input_.excel_folder,
            excel_file_name=input_.excel_file_name,
            sheets=[SheetConfig(name="Videos", columns=input_.video_columns),
                    SheetConfig(name="Bilder", columns=input_.picture_columns)]
        )
        path = create_emtpy_excel(config=config, override=override)
        self.new_message_raw.emit("Excel-Datei erfolgreich erstellt")
        return path

    @pyqtSlot(Path, Path)
    def fill_excel(self, raw: Path, excel: Path):
        if not validate_folder(raw):
            self.problem_with_input.emit(str("!!!! Fehler !!!"))
            return
        errors = validate_excel_file(excel)
        if errors:
            self._send_results_raw(part="Dateien in Excel schreiben.", result=errors)
            return

        result = fill_excel(excel=excel,
                            raw_material_folder=raw)
        self._send_results_raw(part="Dateien in Excel schreiben.", result=result)
        self.process_finished.emit("Dateien in Excel schreiben abgeschlossen.")

    @pyqtSlot(Path, Path)
    def create_picture_folder(self, raw, folder):
        if not validate_folder(raw) or not validate_folder(folder):
            self.problem_with_input.emit(str("!!!! Fehler !!!"))
            return

        result = create_picture_folder(picture_folder=folder,
                                       raw_material_folder=raw)

        self._send_results_raw(part="Bilderordner erstellen.", result=result)
        self.process_finished.emit("Bilderordner erstellen abgeschlossen.")

    # ### UTIL ### #
    @staticmethod
    def _validate_and_prepare(raw_material_folder: Path, excel_full_filepath: Path) -> Dict[str, pd.DataFrame]:
        valid, errors = validation.validate_util_paths(raw_material_folder=raw_material_folder,
                                                       excel_full_filepath=excel_full_filepath)
        if not valid:
            raise ValueError('\n'.join(errors))
        return eval_.prepare_dataframes(excel_file=excel_full_filepath,
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
        self.process_finished.emit("Abschnitte abgeschlossen.")

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
            result = eval_.copy_section(df=df, rating_limit=rating)
            self._send_results_excel(part=f"{part}abschnitte erstellt.", result=result)

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
        self.process_finished.emit("Selektionen abgeschlossen.")

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
            result = eval_.copy_selections(df=df,
                                           raw_path=raw_path,
                                           columns=columns,
                                           marker=marker)
            self._send_results_excel(part=f"{part}selektionen erstellt.", result=result)

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
        self.process_finished.emit("Suche abgeschlossen.")

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
            result = eval_.search_columns(df=df,
                                          raw_path=raw_path,
                                          columns=columns,
                                          markers=keywords,
                                          rating=rating)
            self._send_results_excel(part=f"{part}suche erstellt.", result=result)

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
        self.process_finished.emit("Bilderordner abgeschlossen.")

    def _handle_picture_folder(self, sheets: Dict[str, pd.DataFrame], inputs: UtilTabInput):
        result = eval_.copy_pictures_with_rating(df=sheets["Bilder"],
                                                 raw_path=inputs.raw_material_folder,
                                                 rating_limit=inputs.rating_pictures)
        self._send_results_excel(part="Bilderordner erstellt.", result=result)

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
            #    outfile.write('\n'.join(result))

            self.process_finished.emit("Statistik fertig.")
        except Exception as e:
            self.problem_with_input.emit(str(e))
            return

    def _send_results_raw(self, part: str, result: List[str]):
        self.new_message_raw.emit(part)
        if result:
            self.new_message_raw.emit("Probleme:")
        [self.new_message_raw.emit(f"- {x}") for x in result if x]

    def _send_results_excel(self, part: str, result: List[str]):
        self.new_message_excel.emit(part)
        if result:
            self.new_message_excel.emit("Probleme:")
        [self.new_message_excel.emit(f"- {x}") for x in result if x]
