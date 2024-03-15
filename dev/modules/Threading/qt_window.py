import time

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from qt_worker import Worker


class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__()

        self.initUi()
        self.setup_thread_connections()

    def initUi(self):
        layout = QVBoxLayout()
        self.button = QPushButton("User input")
        self.button.setEnabled(True)

        self.print_label = QtWidgets.QLabel()
        self.print_label.setObjectName("print_label")
        self.print_label.setText("Some Text")

        self.label = QtWidgets.QLabel()
        self.label.setGeometry(QtCore.QRect(25, 25, 200, 200))
        self.label.setMinimumSize(QtCore.QSize(200, 200))
        self.label.setMaximumSize(QtCore.QSize(200, 200))
        self.label.setObjectName("label")

        layout.addWidget(self.button)
        layout.addWidget(self.print_label)
        layout.addWidget(self.label)
        self.setLayout(layout)

        # self.movie = QMovie("output-onlinegiftools.gif")
        # self.label.setMovie(self.movie)

        self.show()

    def setup_thread_connections(self):
        self.thread = QThread()
        self.worker = Worker(ui=self)
        self.worker.moveToThread(self.thread)

        self.button.clicked.connect(lambda: self.worker.some_process(name="halle"))

        self.worker.partial_completion.connect(self.some_process_done)
        self.worker.process_completed.connect(self.process_complete)

        self.thread.start()

    def bla(self):
        self.worker.some_process()

    @pyqtSlot(str)
    def some_process_done(self, msg):
        self.print_label.setText(msg)

    @pyqtSlot()
    def process_complete(self):
        self.print_label.setText("Process complet")


if __name__ == "__main__":
    app = QApplication([])
    w = Window()
    app.exec_()
