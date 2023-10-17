from typing import List

from PyQt5.QtCore import *


class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread.
    Supported Signals:
    """
    problem_with_input = pyqtSignal(str)
    new_message = pyqtSignal(str)
    finished = pyqtSignal()


class Worker(QRunnable):

    def __init__(self, function, *args, **kwargs):
        super(Worker, self).__init__()

        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.kwargs['progress_callback'] = self.signals.new_message

    @pyqtSlot()
    def run(self) -> None:
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.signals.new_message.emit("Start processing")
            result = self.function(*self.args, **self.kwargs)
        except Exception as e:
            print(e)
            self.signals.problem_with_input.emit(f"Problem:\n{str(e)}")
        else:
            # TODO + result is None
            if type(result) == list:
                self.send_result_list("", result)
            else:
                self.signals.new_message.emit(str(result))
        finally:
            self.signals.new_message.emit("Done")
            self.signals.finished.emit()

    def send_result_list(self, part: str, result: List[str]):
        self.signals.new_message.emit(part)
        if result:
            self.signals.new_message.emit("Probleme:")
        [self.signals.new_message.emit(f"- {x}") for x in result if x]
