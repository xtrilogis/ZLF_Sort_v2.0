import time
from PyQt5.QtCore import *

from inputhandling import validation
from foldersetup import folder_structure


class Worker(QThread):
    problem_with_input = pyqtSignal(str)
    new_message_setup = pyqtSignal(str)

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


    @pyqtSlot(str)
    def some_process(self, msg):
        print(msg)
        print("Start processing")
        self.do_task_one()
        print("first block finished")
        self.new_message.emit("partial")

        self.do_task_tow()
        print("finished processing")
        self.new_message.emit("full")

    @pyqtSlot()
    def some_process2(self):
        print("Start processing")
        self.do_task_one()
        print("first block finished")
        self.new_message.emit("partial2")

        self.do_task_tow()
        print("finished processing")
        self.new_message.emit("full2")

    @staticmethod
    def do_task_one():
        time.sleep(3)

    @staticmethod
    def do_task_tow():
        time.sleep(4)
