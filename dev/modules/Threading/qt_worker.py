import time

from PyQt5.QtCore import *


class Worker(QThread):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui

    partial_completion = pyqtSignal(str)
    process_completed = pyqtSignal()

    @pyqtSlot(str)
    def some_process(self, name):
        print(name)
        print("Start processing")
        self.partial_completion.emit("Start")
        self.do_task_one()
        print("first block finished")
        self.partial_completion.emit("first block finished")
        self.do_task_tow()
        print("finished processing")
        self.process_completed.emit()

    @staticmethod
    def do_task_one():
        time.sleep(3)

    @staticmethod
    def do_task_tow():
        time.sleep(6)
