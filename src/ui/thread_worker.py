from pathlib import Path

from PyQt5.QtCore import *

from inputhandling import validation
from foldersetup import folder_structure


class Worker(QThread):
    problem_with_input = pyqtSignal(str)
    new_message_setup = pyqtSignal(str)
    process_finished = pyqtSignal()

    @pyqtSlot(str, QDate)
    def setup_folder_structure(self, parent: str, date: QDate):
        """Create the folder 'Zeltlagerfilm xxxx with all its Subfolders"""
        valid, error = validation.validate_setup(harddrive=parent, date=date)
        if valid:
            self.new_message_setup.emit("Input validiert.")
            folder_structure.create_folder_structure(parent=parent, date=date)
            self.new_message_setup.emit("Ordner erfolgreich erstellt.")
        else:
            self.problem_with_input.emit(error)
        self.process_finished.emit()

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
    def create_excel(self):
        # validation
        # take input an create accordinglly
        # Enum ?
        pass

    @pyqtSlot()
    def fill_excel(self):
        print("Test")
        pass

    @pyqtSlot()
    def create_picture_folder(self):
        pass
