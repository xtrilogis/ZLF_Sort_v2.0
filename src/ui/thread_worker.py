from pathlib import Path
from typing import List

from PyQt5.QtCore import *

from assethandling.asset_manager import settings
from excel import excelmethods
from inputhandling import validation
from foldersetup import folder_structure
from excel.excelmethods import create_emtpy_excel
from assethandling.basemodels import ExcelOptions, SheetConfig, FolderTabInput, UtilTabInput
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
        valid, error = validation.validate_setup(harddrive=inputs.folder, date=inputs.date)
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
        print("Test")
        pass

    @pyqtSlot()
    def create_picture_folder(self):
        pass

    # ### UTIL ### #
    @pyqtSlot(UtilTabInput)
    def full_util_tab(self, inputs: UtilTabInput):
        # TODO handle problem in one part of the execution
        # Validate logic
        valid, errors = validation.validate_util()  # TODO
        if valid:
            try:
                sheets = eval.prepare_dataframes(excel_file=inputs.excel_full_filepath,
                                                 raw_path=inputs.raw_material_folder)
                video_df = sheets["Videos"]
                picture_df = sheets["Bilder"]

                self.new_message_excel.emit("Inputs validiert und Excel eingelesen.")

                if inputs.do_sections:
                    if inputs.do_video_sections:
                        eval.copy_section(video_df, inputs.rating_section)
                        self.new_message_excel.emit("Videoabschnitte erstellt.")
                    if inputs.do_picture_sections:
                        eval.copy_section(picture_df, inputs.rating_section)
                        self.new_message_excel.emit("Bilderabschnitte erstellt.")
                if inputs.do_selections:
                    pass
                if inputs.do_search:
                    pass
                if inputs.create_picture_folder:
                    pass
                self.process_finished.emit("BlaBla: util gesamt fertig")

            except (IndexError, KeyError):
                self.problem_with_input.emit("Fehler beim laden der Excel-Datei.")
        else:
            self.problem_with_input.emit(errors)