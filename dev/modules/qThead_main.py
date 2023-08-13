import time
from PyQt5.QtCore import *


class Worker(QThread):
    partial_completion = pyqtSignal()
    process_completed = pyqtSignal()

    @pyqtSlot()
    def some_process(self):
        print("Start processing")
        self.do_task_one()
        print("first block finished")
        self.partial_completion.emit()
        self.do_task_tow()
        print("finished processing")
        self.process_completed.emit()

    @staticmethod
    def do_task_one():
        time.sleep(3)

    @staticmethod
    def do_task_tow():
        time.sleep(6)