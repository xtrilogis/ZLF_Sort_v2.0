"""Start der App"""
print("Python Code Starting")
from PyQt5.QtCore import QThread, pyqtSlot

from ui.thread_worker import Worker
from ui.popups import messageboxes


from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLineEdit


class MainWindow(QMainWindow):
    """Class handels UI interaction and input."""
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow(self)
        self.thread = QThread()
        self.worker = Worker()
        self.setup_thread_connections()
        self.setup_button_connections()
        self.set_responsive_styles()

    def set_responsive_styles(self):
        self.show_frame()
        self.ui.comboBox.currentIndexChanged.connect(self.show_frame)
        # TODO
        self.ui.harddrive_drop_2.textChanged.connect(lambda text: self.ui.harddrive_drop_2.setStyleSheet(
            "QLineEdit { background-color: %s}" % ('green' if text else 'red')))

    def show_frame(self):
        text = self.ui.comboBox.currentText()
        if text == "Standard":
            self.ui.help_standard_excel.show()
            self.ui.excel_path.hide()
            self.ui.manuel_columns.hide()

        elif "Vorhanden" in text:
            self.ui.help_standard_excel.hide()
            self.ui.excel_path.show()
            self.ui.manuel_columns.hide()
        else:
            self.ui.excel_path.hide()
            self.ui.manuel_columns.show()
            self.ui.help_standard_excel.hide()

    def setup_thread_connections(self):
        self.worker.moveToThread(self.thread)

        # Signal & Slot connections
        self.worker.new_message_setup.connect(self.write_process_setup)
        self.worker.problem_with_input.connect(self.open_problem_input)
        self.worker.process_finished.connect(self.process_finished)

        self.thread.start()

    def setup_button_connections(self):
        # ##### BUTTONS "Ordner erstellt" ##### #
        self.ui.folder_help_pb_2.clicked.connect(self.show_help_folder)
        self.ui.harddrive_tb_2.clicked.connect(self.show_filedialog_harddrive_path)
        self.ui.folder_start_pb_2.clicked.connect(self.setup_folder_structure_new)

        # ##### BUTTONS "Rohmaterial verarbeiten" ##### #
        self.ui.rawpath_folder_tb_2.clicked.connect(
            lambda: self.show_filedialog_raw_material_path(self.ui.rawpath_drop_2))
        self.ui.execute_raw_pB.clicked.connect(self.process_raw_full)
        self.ui.raw_help_pb.clicked.connect(self.show_help_raw)

        self.ui.correct_fs.clicked.connect(
            lambda: self.worker.correct_file_structure(path="")  # TODO
        )

        # ### Excel File
        self.ui.excelpath_folder_tb_2.clicked.connect(
            lambda: self.show_filedialog_excel_file_path(self.ui.excelpath_drop_2))
        self.ui.vid_sugestions_pb.clicked.connect(self.show_suggestions_video)
        self.ui.pic_sugestions_pb.clicked.connect(self.show_suggestions_pictures)
        self.ui.create_excel_pb.clicked.connect(
            lambda: self.worker.create_excel()  # TODO ggf. eigene Function, Variante übergeben
        )
        self.ui.fill_excel_pb.clicked.connect(
            lambda: self.worker.fill_excel()  # TODO
        )
        self.ui.create_picture_folder_pb.clicked.connect(
            lambda: self.worker.create_picture_folder()  # TODO
        )

    # ##### GENERAL METHODS ##### #
    def disable_work_buttons(self):
        """Disable all Buttons which would start another Thread execution."""
        # TODO
        pass

    def enable_work_buttons(self):
        # TODO
        pass

    # ##### PyQt Slots ##### #
    @pyqtSlot(str)
    def write_process_setup(self, msg):
        """Writes the latest status message to the print label."""
        self.ui.print_label_setup.setText(msg)

    @pyqtSlot(str)
    def write_process_raw(self, msg):
        self.ui.print_label.setText(msg)

    @pyqtSlot(str)
    def wirte_process_excel(self, msg):
        pass

    @pyqtSlot(str)
    def open_problem_input(self, error: str):
        """Opens a message box displaying a given error"""
        msg = messageboxes.problem_with_input(error)
        msg.exec()

    @pyqtSlot()
    def process_finished(self):
        self.enable_work_buttons()

    # ##### HELP Button METHODS ##### #
    @staticmethod
    def show_help_folder():
        """Opens a Pop-Up-Window with information about part 1 "Ordner erstellen" """
        msg = messageboxes.help_folder_creation()
        msg.exec()

    @staticmethod
    def show_help_raw():
        """Opens a Pop-Up-Window with information about part 1 "Ordner erstellen" """
        msg = messageboxes.help_raw_material()
        msg.exec()

    # ##### FileDialogs ##### #
    def show_filedialog_harddrive_path(self):
        """Handles selecting the harddrive path/folder through a FileDialog"""
        directory = QFileDialog.getExistingDirectory(parent=self, caption="Open dir", directory="")
        if directory:
            self.ui.harddrive_drop_2.setText(directory)

    def show_filedialog_raw_material_path(self, line_edit: QLineEdit):
        """Handles selecting the raw material path/folder through a FileDialog"""
        directory = QFileDialog.getExistingDirectory(parent=self, caption="Open dir", directory="")
        if directory:
            line_edit.setText(directory)

    def show_filedialog_excel_file_path(self, line_edit: QLineEdit):
        """Handles selecting the Excel file through a FileDialog"""
        directory, _ = QFileDialog.getOpenFileName(parent=self, caption="Open Excel",
                                                   directory="", filter="Excel-Files (*.xlsx)")
        if directory:
            line_edit.setText(directory)

    # ##### PART I: Preset / 'Ordner erstellen' ##### #
    def setup_folder_structure_new(self):
        """Starts process of creating the necessary folders"""
        harddrive = self.ui.harddrive_drop_2.text()
        date = self.ui.dateEdit.date()
        self.worker.setup_folder_structure(parent=harddrive, date=date)

    # ##### PART II: Raw Material / 'Rohmaterial verarbeiten' ##### #
    def get_raw_inputs(self):
        pass
    
    def show_suggestions_video(self):
        # TODO
        # Pop up with select suggestions
        # Fill them into the Line Edit
        pass

    def show_suggestions_pictures(self):
        # TODO
        # Pop up with select suggestions
        # Fill them into the Line Edit
        pass

    def create_excel_file(self):
        # variante, inputs
        # set excel_file_path
        pass

    def process_raw_full(self):
        pass


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    from ui.first_draft import Ui_MainWindow

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
