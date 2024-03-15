import time

from PyQt5.QtCore import *
from PyQt5.QtWidgets import (
    QApplication,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from qtp_worker import Worker

# for reference https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setup_ui()
        self.mutex = QMutex()
        self.cond = QWaitCondition()
        self.threadpool = QThreadPool()
        print(
            "Multithreading with maximum %d threads" % self.threadpool.maxThreadCount()
        )

    def setup_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("This will display results.")
        self.label1 = QLabel("Push the button.")
        button = QPushButton("Start normal")
        button.pressed.connect(self.pushed_button)

        layout.addWidget(self.label)
        layout.addWidget(self.label1)
        layout.addWidget(button)

        self.label2 = QLabel("Push the button")
        button2 = QPushButton("Start")
        button2.pressed.connect(self.pushed_button2)

        layout.addWidget(self.label2)
        layout.addWidget(button2)

        self.label3 = QLabel("This needs some input")
        button3 = QPushButton("Start")
        button3.pressed.connect(self.pushed_button3)

        layout.addWidget(self.label3)
        layout.addWidget(button3)

        w = QWidget()
        w.setLayout(layout)

        self.setCentralWidget(w)

        self.show()

    def progress_fn(self, n):
        self.label.setText(f"Zwischenergebnis {n}")
        print(f"Zwischenergebnis {n}")

    def print_output(self, s):
        self.label.setText(str(s))
        print(s)

    def thread_complete(self):
        self.label.setText("THREAD COMPLETE!")
        print("THREAD COMPLETE!")

    def pushed_button(self):
        # Any other args, kwargs are passed to the run function
        worker = Worker(self.function_no_parameters, self.mutex, self.cond)
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)

    def pushed_button2(self):
        # Any other args, kwargs are passed to the run function
        worker = Worker(
            self.function_with_parameter,
            self.mutex,
            self.cond,
            mydict={"hasl": "asdf", "asfes": "sefsa"},
        )
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)

    def pushed_button3(self):
        # Any other args, kwargs are passed to the run function
        worker = Worker(self.function_with_input, self.mutex, self.cond)
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        worker.signals.request_data.connect(self.input_information)

        # Execute
        self.threadpool.start(worker)

    def input_information(self, text):
        text, ok = QInputDialog.getItem(self, "title", "question", ["Ja", "Nein"])
        # text, ok = QInputDialog().getText(self, "QInputDialog().getText()",
        #                                   text, QLineEdit.Normal,
        #                                   "Input")
        if ok and text:
            self.sender().data_response.emit(text)
        self.cond.wakeAll()

    # All these functions can be placed outside the MainWindow Class
    # or even a different file
    def function_no_parameters(self, progress_callback, get_data):
        for n in range(0, 5):
            progress_callback.emit(str(n * 100 / 4))
            time.sleep(1)
        return "Done."

    def function_with_parameter(self, mydict, progress_callback, get_data):
        for item, key in enumerate(mydict):
            progress_callback.emit(str(item))
            time.sleep(3)
        return "Done."

    def function_with_input(self, progress_callback, get_data):
        for i in range(3):
            progress_callback.emit(str(i))
            time.sleep(1)
        result = get_data(text="Input what ever")
        progress_callback.emit(result)
        time.sleep(1)
        return "Done."


if __name__ == "__main__":
    app = QApplication([])
    w = MainWindow()
    app.exec_()
