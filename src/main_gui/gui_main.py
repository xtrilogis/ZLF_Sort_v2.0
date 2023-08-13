"""Start der App"""
from PyQt5.QtCore import QThread, pyqtSlot

from ui.thread_worker import Worker
from ui.popups import messageboxes

print("Python Code Starting")
from PyQt5.QtWidgets import QMainWindow, QFileDialog


class MainWindow(QMainWindow):
    """Class handels UI interaction and input."""
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow(self)
        self.thread = QThread()
        self.worker = Worker()
        self.setup_thread_connections()
        self.setup_button_connections()

    def setup_thread_connections(self):
        self.worker.moveToThread(self.thread)

        # Signal & Slot connections
        self.worker.new_message_setup.connect(self.write_process_setup)
        self.worker.problem_with_input.connect(self.open_problem_input)

        self.thread.start()

    def setup_button_connections(self):
        # ##### BUTTONS "Ordner erstellt" ##### #
        self.ui.folder_help_pb_2.clicked.connect(self.show_help_folder)
        self.ui.harddrive_tb_2.clicked.connect(self.show_filedialog_harddrive_path)
        self.ui.folder_start_pb_2.clicked.connect(self.setup_folder_structure_new)

    # ##### PyQt Slots ##### #
    @pyqtSlot(str)
    def write_process_setup(self, msg):
        """Writes the latest status message to the print label."""
        self.ui.print_label_setup.setText(msg)

        # # ggf. ein finished Process -> um disabeld wieder frei zu geben

    @pyqtSlot(str)
    def open_problem_input(self, error: str):
        """Opens a message box displaying a given error"""
        msg = messageboxes.problem_with_input(error)
        msg.exec()

    # ##### HELP Button METHODS ##### #
    @staticmethod
    def show_help_folder():
        """Opens a Pop-Up-Window with information about part 1 "Ordner erstellen" """
        msg = messageboxes.help_folder_creation()
        msg.exec()

    # ##### FileDialogs ##### #
    def show_filedialog_harddrive_path(self):
        """Handles selecting the harddrive path/folder through a FileDialog"""
        directory = QFileDialog.getExistingDirectory(parent=self, caption="Open dir", directory="")
        if directory:
            self.ui.harddrive_drop_2.setText(directory)

    # ##### PART I: Preset / 'Ordner erstellen' ##### #
    def setup_folder_structure_new(self):
        """Starts process of creating the necessary folders"""
        harddrive = self.ui.harddrive_drop_2.text()
        print(harddrive)
        date = self.ui.dateEdit.date()
        print(date)
        self.worker.setup_folder_structure(parent=harddrive, date=date)

    def disable_work_buttons(self):
        """Disable all Buttons which would start another Thread execution."""
        pass


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    from ui.first_draft import Ui_MainWindow

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
