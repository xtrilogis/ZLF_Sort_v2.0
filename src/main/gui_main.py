"""Start der App"""
# print("Python Code Starting")
from typing import List

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QLineEdit, QDialog, QPlainTextEdit
from PyQt5.QtCore import *
import sys
from pathlib import Path

from pydantic import ValidationError

from assethandling.basemodels import UtilTabInput
from ui import Ui_MainWindow, messageboxes, Worker, SelectionDialog
from adapt import runners
from inputhandling.validation import validate_excel_file
from excel import excelmethods

print("Imports done")


class MainWindow(QMainWindow):
    """Class handels UI interaction and input."""
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow(self)
        self.setup_ui()
        self.setup_button_connections()
        self.threadpool = QThreadPool()

    def setup_ui(self):
        pass

    def setup_button_connections(self):
        # ##### BUTTONS "Ordner erstellt" ##### #
        self.ui.harddrive_tb_2.clicked.connect(self.show_filedialog_harddrive_path)
        self.ui.folder_start_pb_2.clicked.connect(
            lambda: self.run_button_action(function=runners.execute_function,
                                           slot=self.write_process_setup)
        )

        # ##### BUTTONS "Rohmaterial verarbeiten" ##### #
        self.ui.rawpath_folder_tb_2.clicked.connect(
            lambda: self.show_filedialog_folder(self.ui.rawpath_drop_2))

        # ##### BUTTONS "Auswertung" ##### #
        self.ui.rawpath_folder_tb_3.clicked.connect(
            lambda: self.show_filedialog_folder(self.ui.rawpath_drop_3)
        )
        self.ui.excelpath_folder_tb_3.clicked.connect(
            lambda: self.show_filedialog_excel_file_path(self.ui.excelpath_drop_3)
        )

        self.ui.excel_start_pb_6.clicked.connect(lambda: self.run_util_action(function=runners.run_copy_sections))

    # ##### GENERAL METHODS ##### #
    def disable_work_buttons(self):
        """Disable all Buttons which would start another Thread execution."""
        # TODO
        # Name Buttons with start_...
        pass

    def enable_work_buttons(self):
        # TODO
        pass

    @staticmethod
    def add_label_text(msg, label: QLabel):
        text = label.text()
        label.setText(f"{text}\n{msg}")

    # ##### PyQt Slots ##### #
    @pyqtSlot(str)
    def write_process_setup(self, msg: str):
        """Writes the latest status message to the print label."""
        self.add_label_text(msg=msg, label=self.ui.print_label_setup)

    @pyqtSlot(str)
    def write_process_raw(self, msg):
        self.add_label_text(msg=msg, label=self.ui.print_label)

    @pyqtSlot(str)
    def write_process_util(self, msg):
        self.add_label_text(msg=msg, label=self.ui.print_label_2)

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
        # self.movie.stop()

    # ##### Actions ##### #
    def run_button_action(self, function, slot):
        self.disable_work_buttons()
        # self.movie.start()
        worker = Worker(function)
        worker.signals.new_message.connect(slot)
        worker.signals.problem_with_input.connect(self.open_problem_input)
        worker.signals.finished.connect(self.process_finished)

        self.threadpool.start(worker)

    def run_util_action(self, function):
        try:
            data: UtilTabInput = self.get_util_input()
        except (ValidationError, ValueError) as e:
            self.open_problem_input(error=str(e))
            return
        self.disable_work_buttons()
        # self.movie.start()
        worker = Worker(function, inputs=data)
        worker.signals.new_message.connect(self.write_process_util)
        worker.signals.problem_with_input.connect(self.open_problem_input)
        worker.signals.finished.connect(self.process_finished)

        self.threadpool.start(worker)

    def get_util_input(self):
        if self.ui.rawpath_drop_3.text() == "" or \
                self.ui.excelpath_drop_3.text() == "":
            raise ValueError("Bitte fülle die Felder in 'Input' aus")
        data = {
            "raw_material_folder": Path(self.ui.rawpath_drop_3.text()),
            "excel_full_filepath": Path(self.ui.excelpath_drop_3.text()),
            "do_sections": self.ui.segment.isChecked(),
            "do_video_sections": self.ui.segment_videos_checkB.isChecked(),
            "do_picture_sections": self.ui.segment_picture_checkB.isChecked(),
            "rating_section": self.ui.rating_limit_spinB.value(),
            "do_selections": self.ui.selection.isChecked(),
            "videos_columns_selection": self.get_LineEdit_parts(self.ui.column_videos_linee_3),
            "picture_columns_selection": self.get_LineEdit_parts(self.ui.column_pictures_linee_3),
            "marker": self.ui.marker_linee.text(),
            "do_search": self.ui.selection_2.isChecked(),
            "videos_columns_search": self.get_LineEdit_parts(self.ui.column_videos_linee_2),
            "picture_columns_search": self.get_LineEdit_parts(self.ui.column_pictures_linee_2),
            "keywords": self.get_LineEdit_parts(self.ui.marker_linee_2),
            "rating_search": self.ui.rating_limit_spinB_3.value(),
            "create_picture_folder": self.ui.segment_2.isChecked(),
            "rating_pictures": self.ui.rating_limit_spinB_2.value(),
        }
        return UtilTabInput(**data)

    # ##### FileDialogs ##### #
    def show_filedialog_harddrive_path(self):
        """Handles selecting the harddrive path/folder through a FileDialog"""
        directory = QFileDialog.getExistingDirectory(parent=self, caption="Open dir", directory="")
        if directory:
            self.ui.harddrive_drop_2.setText(directory)

    def show_filedialog_folder(self, line_edit: QLineEdit):
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

    # ##### other ##### #
    def select_columns(self, line_edit: QLineEdit, sheet: str):
        try:
            if self.ui.excelpath_drop_3.text() == "":
                raise ValueError("Bitte gib eine Excel-Datei an.")
            path = Path(self.ui.excelpath_drop_3.text())
            errors = validate_excel_file(excel_file=path)
            if errors:
                raise ValueError('\n'.join(errors))
            items = excelmethods.get_columns(excel=path, sheet=sheet)
            dial = SelectionDialog("Spalten Auswahl", "Spalten", items, self)
            if dial.exec_() == QDialog.Accepted:
                select = dial.itemsSelected()
                text = ", ".join(select)
                line_edit.setText(text)
        except Exception as e:
            self.open_problem_input(error=str(e))

    @staticmethod
    def get_LineEdit_parts(element: QLineEdit) -> List[str]:
        cols = []
        for part in element.text().split(','):
            if part.strip():
                cols.append(part.strip())
        return cols

    @staticmethod
    def get_PlainTextEdit_parts(element: QPlainTextEdit) -> List[str]:
        cols = []
        for part in element.document().toRawText().split(','):
            if part.strip():
                cols.append(part.strip())
        return cols


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
