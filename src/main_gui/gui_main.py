"""Start der App"""
# print("Python Code Starting")
from datetime import datetime
from pathlib import Path
from typing import List

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLineEdit, QDialog
from PyQt5.QtCore import QThread, pyqtSlot

from assethandling.asset_manager import settings
from assethandling.basemodels import ExcelOptions, RawTabInput, UtilTabInput
from ui.dialogs.selection_dialog import SelectionDialog
from ui.thread_worker import Worker
from ui.popups import messageboxes

print("Imports done")


class MainWindow(QMainWindow):
    """Class handels UI interaction and input."""
    raw_input: RawTabInput = None
    util_input: UtilTabInput = None

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow(self)
        self.thread = QThread()
        self.worker = Worker()
        self.setup_ui()
        self.setup_thread_connections()
        self.setup_button_connections()
        self.set_responsive_styles()

    def setup_ui(self):
        self.show_frame()
        # TODO use basemodel input ??
        self.ui.vid_columns.setText(", ".join(settings["standard-video-columns"]))
        self.ui.pic_columns.setPlainText(", ".join(settings["standard-picture-columns"]))
        self.ui.lineEdit.setText(f"Zeltlagerfilm {datetime.now().date().year}.xlsx")
        #self.ui.rawpath_drop_2.textChanged.connect(
        #    lambda: self.ui.excel_folder_drop_4.setText(str(Path(self.ui.rawpath_drop_2.text()).parent))
        #)

    def set_responsive_styles(self):
        self.ui.comboBox.currentIndexChanged.connect(self.show_frame)
        # TODO
        self.ui.harddrive_drop_2.textChanged.connect(lambda text: self.ui.harddrive_drop_2.setStyleSheet(
            "QLineEdit { background-color: %s}" % ('green' if text else 'red')))

    def show_frame(self):
        text = self.ui.comboBox.currentText()
        if text == ExcelOptions.STANDARD.value:
            self.ui.help_standard_excel.show()
            self.ui.excel_path.hide()
            self.ui.manuel_columns.hide()
            self.ui.frame_8.show()
        elif text == ExcelOptions.EXISTING.value:
            self.ui.help_standard_excel.hide()
            self.ui.excel_path.show()
            self.ui.manuel_columns.hide()
            self.ui.frame_8.hide()
        else:
            self.ui.excel_path.hide()
            self.ui.manuel_columns.show()
            self.ui.help_standard_excel.hide()
            self.ui.frame_8.show()

    def setup_thread_connections(self):
        self.worker.moveToThread(self.thread)

        # Signal & Slot connections
        self.worker.new_message_setup.connect(self.write_process_setup)
        self.worker.problem_with_input.connect(self.open_problem_input)
        self.worker.process_finished.connect(self.process_finished)

        self.worker.new_message_raw.connect(self.write_process_raw)
        self.worker.excel_exits_error.connect(self.open_excel_exists)

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
        self.ui.rawpath_folder_tb_4.clicked.connect(
            lambda: self.show_filedialog_raw_material_path(self.ui.excel_folder_drop_4)
        )
        self.ui.vid_sugestions_pb.clicked.connect(self.show_suggestions_video)
        self.ui.pic_sugestions_pb.clicked.connect(self.show_suggestions_pictures)
        self.ui.create_excel_pb.clicked.connect(self.create_excel_file)
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
        # Name Buttons with start_...
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
        self.ui.print_label_2.setText(msg)

    @pyqtSlot(str)
    def open_problem_input(self, error: str):
        """Opens a message box displaying a given error"""
        msg = messageboxes.problem_with_input(error)
        msg.exec()

    @pyqtSlot()
    def open_excel_exists(self):
        """Opens a message box displaying a given error"""
        msg = messageboxes.excel_exists("Die angegebene Excel-Datei existiert bereits.")
        msg.buttonClicked.connect(self.handle_excel_choice)
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
    def handle_excel_choice(self, i):
        if "Überschreiben" in i.text():
            self.create_excel_file(override=True)

    def get_raw_inputs(self):
        pass

    def show_suggestions_video(self):
        dial = SelectionDialog("Vorschläge Video Spalten", "Spalten", settings["suggestions-video-columns"], self)
        if dial.exec_() == QDialog.Accepted:
            select = dial.itemsSelected()
            columns: List[str] = settings["standard-video-columns"].copy()
            columns.extend(select)
            text = ", ".join(columns)
            self.ui.vid_columns.setText(text)

    def show_suggestions_pictures(self):
        dial = SelectionDialog("Vorschläge Bilder Spalten", "Spalten", settings["suggestions-picture-columns"], self)
        if dial.exec_() == QDialog.Accepted:
            select = dial.itemsSelected()
            columns: List[str] = settings["standard-picture-columns"].copy()
            columns.extend(select)
            text = ", ".join(columns)
            self.ui.pic_columns.setPlainText(text)

    def create_excel_file(self, override=False):
        text = self.ui.comboBox.currentText()
        if text == ExcelOptions.EXISTING.value:
            # set marker
            pass
        else:
            if self.ui.excel_folder_drop_4.text() == "":
                error = "Bitte gib einen Speicherort für die Excel-Datei an.\n" \
                        "Dazu kannst du bei 'Excel-Datei' einen Ordner \n" \
                        "angeben oder für den Standardweg den Rohmaterialorder \nangeben." \
                        "Für Standards schau dir doch gerne die Anleitung an."
                msg = messageboxes.problem_with_input(error)
                msg.exec()
            file_name = self.ui.lineEdit.text()
            path = Path(self.ui.excel_folder_drop_4.text())
            if text == ExcelOptions.STANDARD.value:
                self.worker.create_excel(file_name=file_name, path=path, override=override)
            else:
                self.worker.create_excel(file_name=file_name,
                                         path=path,
                                         option=ExcelOptions.MANUAL,
                                         columns=[
                                             self.ui.vid_columns.text().split(", "),
                                             self.ui.pic_columns.text().split(", ")
                                         ],
                                         override=override)

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
