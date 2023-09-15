import time
from pathlib import Path

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QApplication, QMainWindow, QLabel
from PyQt5 import QtCore
from PyQt5.QtCore import *
from qtp_worker import Worker
from src.inputhandling.validation import is_valid_folder
# https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setup_ui()
        self.counter = 0
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def setup_ui(self):
        layout = QVBoxLayout()

        self.l = QLabel("Start")
        b = QPushButton("DANGER!")
        b.pressed.connect(self.oh_no)

        layout.addWidget(self.l)
        layout.addWidget(b)

        w = QWidget()
        w.setLayout(layout)

        self.setCentralWidget(w)

        self.show()

    def progress_fn(self, n):
        self.l.setText("%d%% done" % n)
        print("%d%% done" % n)

    def execute_this_fn(self, progress_callback):
        for n in range(0, 5):
            time.sleep(1)
            progress_callback.emit(n*100/4)

        return "Done."

    def execute_another_fn(self, mydict, progress_callback):
        for item, key in enumerate(mydict):
            progress_callback.emit(item)
            time.sleep(3)

    def print_output(self, s):
        self.l.setText(str(s))
        print(s)

    def thread_complete(self):
        self.l.setText("THREAD COMPLETE!")
        print("THREAD COMPLETE!")

    def oh_no(self):
        # Pass the function to execute
        worker = Worker(is_valid_folder, element=Path("D:"))  # self.execute_another_fn, mydict={"hasl": "asdf", "asfes": "sefsa"}) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)


if __name__ == "__main__":
    app = QApplication([])
    w = MainWindow()
    app.exec_()
