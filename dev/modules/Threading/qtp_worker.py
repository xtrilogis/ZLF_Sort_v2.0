from PyQt5.QtCore import *
import traceback
import sys


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished No data
    error tuple (exc_type, value, traceback.format_exc() )
    result object data returned from processing, anything
    progress int indicating % progress
    request_data str to be displayed on the InputDialog
    data_response str containing the response
    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(str)
    request_data = pyqtSignal(str)
    data_response = pyqtSignal(str)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param fn: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type fn: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """

    def __init__(self, fn, mutex, cond, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.mtx = mutex  # Those are needed for freezing the thread
        self.cond = cond  # while waiting for the input
        self.args = args
        self.kwargs = kwargs

        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress
        # Add the get_data function to enable requesting input
        self.kwargs['get_data'] = self.get_input
        self.signals.data_response.connect(self.set_input)
        self.user_input = None

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exc_type, value = sys.exc_info()[:2]
            self.signals.error.emit((exc_type, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

    def get_input(self, text):
        self.signals.request_data.emit(text)
        self.mtx.lock()
        try:
            self.cond.wait(self.mtx)
        finally:
            self.mtx.unlock()
        return self.user_input

    def set_input(self, input_):
        self.user_input = input_
