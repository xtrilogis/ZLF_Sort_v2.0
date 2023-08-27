from pathlib import Path
from typing import List

from PyQt5.QtCore import *

from assethandling.asset_manager import settings
from inputhandling import validation
from foldersetup import folder_structure
from excel.excelmethods import create_emtpy_excel
from assethandling.basemodels import ExcelOptions, SheetConfig, FolderTabInput


class Worker(QThread):
    problem_with_input = pyqtSignal(str)
    process_finished = pyqtSignal(str)

    new_message_setup = pyqtSignal(str)

    new_message_raw = pyqtSignal(str)
    excel_exits_error = pyqtSignal()

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
