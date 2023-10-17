"""Start der App"""
# print("Python Code Starting")
import traceback
from datetime import datetime
from typing import List

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QLineEdit, QDialog, QPlainTextEdit
from PyQt5.QtCore import *
import sys
from pathlib import Path

from pydantic import ValidationError

from assethandling.asset_manager import settings
from assethandling.basemodels import UtilTabInput, RawTabInput, FolderTabInput, ExcelOptions, ExcelInput
from ui import Ui_MainWindow, messageboxes, Worker, SelectionDialog
from adapt import runners
from inputhandling.validation import validate_excel_file
from excel import excelmethods
from assethandling.asset_manager import gif


print("Imports done")


class MainWindow(QMainWindow):
    """Class handels UI interaction and input."""
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow(self)
        self.setup_ui()
        self.setup_button_connections()
        self.threadpool = QThreadPool()
        self.current_function = None

        self.movie = QtGui.QMovie(gif)
        self.ui.process_gif_label.setMovie(self.movie)
        self.ui.process_gif_label_2.setMovie(self.movie)
        self.movie.start()
        self.movie.stop()

    def setup_ui(self):
        self.ui.tabWidget.setCurrentIndex(0)
        # Setup Start
        self.ui.date_lkw.setDate(QDate.currentDate())
        self.ui.date_correct_fs.setDate(QDate.currentDate())
        # setup Raw
        self.ui.tabWidget_raw.setCurrentIndex(0)
        self.show_frame()
        self.ui.excel_option.currentIndexChanged.connect(self.show_frame)
        self.ui.vid_columns.setPlainText(", ".join(settings["standard-video-columns"]))
        self.ui.pic_columns.setPlainText(", ".join(settings["standard-picture-columns"]))
        self.ui.le_excel_file_name.setText(f"Zeltlagerfilm {datetime.now().date().year}.xlsx")

        self.setup_responsive_styles()

    def show_frame(self):
        text = self.ui.excel_option.currentText()
        if text == ExcelOptions.STANDARD.value:
            self.ui.help_standard_excel.show()
            self.ui.excel_path.hide()
            self.ui.manuel_columns.hide()
            self.ui.frame_8.show()
            self.ui.pb_create_excel.show()
        elif text == ExcelOptions.EXISTING.value:
            self.ui.help_standard_excel.hide()
            self.ui.excel_path.show()
            self.ui.manuel_columns.hide()
            self.ui.frame_8.hide()
            self.ui.pb_create_excel.hide()
        else:
            self.ui.excel_path.hide()
            self.ui.manuel_columns.show()
            self.ui.help_standard_excel.hide()
            self.ui.frame_8.show()
            self.ui.pb_create_excel.show()

    def setup_responsive_styles(self):
        self.ui.drop_util_excelfile.setStyleSheet("QLineEdit { color: 'red';}")
        self.ui.drop_util_rawpath.setStyleSheet("QLineEdit { color: 'red';}")
        self.ui.drop_raw_rawpath.setStyleSheet("QLineEdit { color: 'red';}")
        self.ui.drop_raw_excel_file.setStyleSheet("QLineEdit { color: 'red';}")
        self.ui.drop_picture_folder.setStyleSheet("QLineEdit { color: 'red';}")
        self.ui.drop_harddrive.setStyleSheet("QLineEdit { color: 'red';}")

        self.ui.drop_util_excelfile.textChanged.connect(
            lambda text: self.ui.drop_util_excelfile.setStyleSheet(
                "QLineEdit { color: %s}" % ('green' if text else 'red')))
        self.ui.drop_util_rawpath.textChanged.connect(
            lambda text: self.ui.drop_util_rawpath.setStyleSheet(
                "QLineEdit { color: %s}" % ('green' if text else 'red')))
        self.ui.drop_raw_rawpath.textChanged.connect(
            lambda text: self.ui.drop_raw_rawpath.setStyleSheet(
                "QLineEdit { color: %s}" % ('green' if text else 'red')))
        self.ui.drop_raw_excel_file.textChanged.connect(
            lambda text: self.ui.drop_raw_excel_file.setStyleSheet(
                "QLineEdit { color: %s}" % ('green' if text else 'red')))
        self.ui.drop_picture_folder.textChanged.connect(
            lambda text: self.ui.drop_picture_folder.setStyleSheet(
                "QLineEdit { color: %s}" % ('green' if text else 'red')))
        self.ui.drop_harddrive.textChanged.connect(
            lambda text: self.ui.drop_harddrive.setStyleSheet(
                "QLineEdit { color: %s}" % ('green' if text else 'red')))

    def setup_button_connections(self):
        # ##### BUTTONS "Ordner erstellt" ##### #
        self.ui.tb_harddrive.clicked.connect(self.show_filedialog_harddrive_path)
        self.ui.pb_foldersetup.clicked.connect(
            lambda: self.run_folder_setup(function=runners.run_folder_setup))

        # ##### BUTTONS "Rohmaterial verarbeiten" ##### #
        self.ui.tb_raw_rawpath.clicked.connect(
            lambda: self.show_filedialog_folder(self.ui.drop_raw_rawpath))
        self.ui.pb_start_raw_full.clicked.connect(
            lambda: self.raw_with_excel(function=runners.run_process_raw_full))
        self.ui.pb_correct_fs.clicked.connect(
            lambda: self.run_raw_action(function=runners.run_correct_structure))
        self.ui.pb_rename.clicked.connect(
            lambda: self.run_raw_action(function=runners.run_rename_files))

        self.ui.pb_create_excel.clicked.connect(
            lambda: self.raw_with_excel(function=runners.create_excel))
        self.ui.pb_fill_excel.clicked.connect(
            lambda: self.raw_with_excel(function=runners.run_fill_excel))

        self.ui.pb_vid_sugestions.clicked.connect(
            lambda: self.show_suggestions(text_edit=self.ui.vid_columns,
                                          suggestions=settings["suggestions-video-columns"])
        )
        self.ui.pb_pic_sugestions.clicked.connect(
            lambda: self.show_suggestions(text_edit=self.ui.pic_columns,
                                          suggestions=settings["suggestions-picture-columns"])
        )
        self.ui.tb_excel_folder.clicked.connect(
            lambda: self.show_filedialog_folder(self.ui.drop_excel_folder)
        )
        self.ui.tb_raw_excel_file.clicked.connect(
            lambda: self.show_filedialog_excel_file_path(self.ui.drop_raw_excel_file)
        )

        self.ui.tb_picture_folder.clicked.connect(
            lambda: self.show_filedialog_folder(self.ui.drop_picture_folder)
        )
        self.ui.pb_create_picture_folder.clicked.connect(
            lambda: self.run_raw_action(function=runners.run_create_picture_folder)
        )

        # ##### BUTTONS "Auswertung" ##### #
        self.ui.tb_util_rawpath.clicked.connect(
            lambda: self.show_filedialog_folder(self.ui.drop_util_rawpath)
        )
        self.ui.tb_util_excelfile.clicked.connect(
            lambda: self.show_filedialog_excel_file_path(self.ui.drop_util_excelfile)
        )

        self.ui.pb_section.clicked.connect(
            lambda: self.run_util_action(function=runners.run_copy_sections))
        self.ui.pb_start_selection.clicked.connect(
            lambda: self.run_util_action(function=runners.run_copy_selection))
        self.ui.pb_search.clicked.connect(
            lambda: self.run_util_action(function=runners.run_search))
        self.ui.pb_picturefolder.clicked.connect(
            lambda: self.run_util_action(function=runners.run_create_rated_picture_folder))
        self.ui.pb_util_all.clicked.connect(
            lambda: self.run_util_action(function=runners.run_process_util_full))
        self.ui.pb_statistic.clicked.connect(
            lambda: self.run_util_action(function=runners.run_statistics))

        self.ui.pb_select_pic_columns.clicked.connect(
            lambda: self.select_columns(line_edit=self.ui.le_selection_pic_columns, sheet="Bilder")
        )
        self.ui.pb_select_vid_columns.clicked.connect(
            lambda: self.select_columns(line_edit=self.ui.le_selection_vid_columns, sheet="Videos")
        )
        self.ui.pb_search_pic_columns.clicked.connect(
            lambda: self.select_columns(line_edit=self.ui.le_search_pic_columns, sheet="Bilder")
        )
        self.ui.pb_search_vid_columns.clicked.connect(
            lambda: self.select_columns(line_edit=self.ui.le_search_vid_columns, sheet="Videos")
        )

    # ##### GENERAL METHODS ##### #
    def disable_work_buttons(self):
        """Disable all Buttons which would start another Thread execution."""
        # ##### BUTTONS "Ordner erstellt" ##### #
        self.ui.pb_foldersetup.setEnabled(False)

        # ##### BUTTONS "Rohmaterial verarbeiten" ##### #

        self.ui.pb_start_raw_full.setEnabled(False)
        self.ui.pb_correct_fs.setEnabled(False)
        self.ui.pb_rename.setEnabled(False)

        self.ui.pb_create_excel.setEnabled(False)
        self.ui.pb_fill_excel.setEnabled(False)

        self.ui.pb_create_picture_folder.setEnabled(False)

        # ##### BUTTONS "Auswertung" ##### #
        self.ui.pb_section.setEnabled(False)
        self.ui.pb_start_selection.setEnabled(False)
        self.ui.pb_search.setEnabled(False)
        self.ui.pb_picturefolder.setEnabled(False)
        self.ui.pb_util_all.setEnabled(False)
        self.ui.pb_statistic.setEnabled(False)

    def enable_work_buttons(self):
        # ##### BUTTONS "Ordner erstellt" ##### #
        self.ui.pb_foldersetup.setEnabled(True)

        # ##### BUTTONS "Rohmaterial verarbeiten" ##### #

        self.ui.pb_start_raw_full.setEnabled(True)
        self.ui.pb_correct_fs.setEnabled(True)
        self.ui.pb_rename.setEnabled(True)

        self.ui.pb_create_excel.setEnabled(True)
        self.ui.pb_fill_excel.setEnabled(True)

        self.ui.pb_create_picture_folder.setEnabled(True)

        # ##### BUTTONS "Auswertung" ##### #
        self.ui.pb_section.setEnabled(True)
        self.ui.pb_start_selection.setEnabled(True)
        self.ui.pb_search.setEnabled(True)
        self.ui.pb_picturefolder.setEnabled(True)
        self.ui.pb_util_all.setEnabled(True)
        self.ui.pb_statistic.setEnabled(True)

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
        self.add_label_text(msg=msg, label=self.ui.print_labelraw)

    @pyqtSlot(str)
    def write_process_util(self, msg):
        self.add_label_text(msg=msg, label=self.ui.print_label_util)

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

    def handle_excel_choice(self, i):
        if "Überschreiben" in i.text():
            self.raw_with_excel(function=self.current_function, override=True)

    @pyqtSlot()
    def process_finished(self):
        self.enable_work_buttons()
        self.movie.stop()

    # ##### Actions ##### #
    def run_folder_setup(self, function):
        try:
            if self.ui.drop_harddrive.text() == "":
                self.open_problem_input(error="Bitte gib einen Dateipfad an.")
                return
            data = FolderTabInput(
                folder=Path(self.ui.drop_harddrive.text()),
                date=self.ui.date_lkw.date().toPyDate()
            )
        except ValidationError as e:
            traceback.print_exc()
            self.open_problem_input(msg=str(e))
            return
        self.run_action(function=function, slot=self.write_process_setup, input_=data)

    def run_raw_action(self, function):
        try:
            self.current_function = function
            data: RawTabInput = self.get_raw_input()
        except (ValidationError, ValueError) as e:
            traceback.print_exc()
            self.open_problem_input(error=str(e))
            return
        self.current_function = None
        self.run_action(function=function, slot=self.write_process_raw, input_=data)

    def get_raw_input(self, excel=None) -> RawTabInput:
        data = {
            "do_structure": self.ui.cb_structure.isChecked(),
            "do_rename": self.ui.cb_rename.isChecked(),
            "fill_excel": self.ui.cb_fill_excel.isChecked(),
            "create_picture_folder": self.ui.cb_diashow.isChecked(),
            "raw_material_folder": Path(self.ui.drop_raw_rawpath.text()),
            "first_folder_date": self.ui.date_correct_fs.date().toPyDate(),
            "excel": excel,
        }
        if self.ui.custom_picture_folder.isChecked():
            if self.ui.drop_picture_folder.text() == "":
                raise ValueError("Bitte gib einen Speicherort für den Bilderordner an.")
            data["picture_folder"] = Path(self.ui.drop_picture_folder.text())
        else:
            data["picture_folder"] = data.get("raw_material_folder").parent / "Bilderordner"

        return RawTabInput(**data)

    def raw_with_excel(self, function, override=False):
        try:
            self.current_function = function
            data: RawTabInput = self.get_raw_input(self.excel(override=override))
        except (ValidationError, ValueError) as e:
            traceback.print_exc()
            self.open_problem_input(error=str(e))
            return
        self.current_function = None
        self.run_action(function=function, slot=self.write_process_raw, input_=data)

    def excel(self, override) -> Path | ExcelInput | None:
        if not self.ui.cb_fill_excel:
            return None
        excel_option: ExcelOptions = ExcelOptions(self.ui.excel_option.currentText())
        if excel_option == ExcelOptions.EXISTING:
            return Path(self.ui.drop_raw_excel_file.text())
        else:
            try:
                config = self._get_excel_input(option=excel_option)
                config.override = override
                if (config.excel_folder / config.excel_file_name).exists() and not override:
                    self.open_excel_exists()
                    return
                return config
            except Exception as e:
                traceback.print_exc()
                self.open_problem_input(str(e))

    def _get_excel_input(self, option) -> ExcelInput:
        if option != ExcelOptions.STANDARD and option != ExcelOptions.MANUAL:
            error = "Interner Fehler, der Button 'Excel erstellen'\n" \
                    "sollte nicht klickbar sein mit der Option \n" \
                    "vorhandene Excel nutzen. Neustarten."
            raise ValueError(error)
        elif self.ui.drop_raw_rawpath.text() == "":
            error = "Bitte gib einen Speicherort für die Excel-Datei an.\n" \
                    "Dazu kannst du bei 'Excel-Datei' einen Ordner \n" \
                    "angeben oder für den Standardweg den Rohmaterialorder \nangeben." \
                    "Für Standards schau dir doch gerne die Anleitung an."
            raise ValueError(error)
        else:
            if option == ExcelOptions.MANUAL:
                config = ExcelInput(
                    excel_folder=Path(self.ui.drop_excel_folder.text()),
                    excel_file_name=self.ui.le_excel_file_name.text(),
                    video_columns=self.get_PlainTextEdit_parts(self.ui.vid_columns),
                    picture_columns=self.get_PlainTextEdit_parts(self.ui.pic_columns)
                )
            else:
                config = ExcelInput(
                    excel_folder=Path(self.ui.drop_raw_rawpath.text())
                )
            return config

    def run_util_action(self, function):
        try:
            data: UtilTabInput = self.get_util_input()
        except (ValidationError, ValueError) as e:
            traceback.print_exc()
            self.open_problem_input(error=str(e))
            return
        self.run_action(function=function, slot=self.write_process_util, input_=data)

    def run_action(self, function, slot, input_):
        self.disable_work_buttons()
        self.movie.start()
        worker = Worker(function, inputs=input_)
        worker.signals.new_message.connect(slot)
        worker.signals.problem_with_input.connect(self.open_problem_input)
        worker.signals.finished.connect(self.process_finished)

        self.threadpool.start(worker)

    def get_util_input(self) -> UtilTabInput:
        if self.ui.drop_util_rawpath.text() == "" or \
                self.ui.drop_util_excelfile.text() == "":
            raise ValueError("Bitte fülle die Felder in 'Input' aus")
        data = {
            "raw_material_folder": Path(self.ui.drop_util_rawpath.text()),
            "excel_full_filepath": Path(self.ui.drop_util_excelfile.text()),
            "do_sections": self.ui.section.isChecked(),
            "do_video_sections": self.ui.cb_segment_videos.isChecked(),
            "do_picture_sections": self.ui.cb_segment_picture.isChecked(),
            "rating_section": self.ui.sb_rating_section.value(),
            "do_selections": self.ui.selection.isChecked(),
            "videos_columns_selection": self.get_LineEdit_parts(self.ui.le_selection_vid_columns),
            "picture_columns_selection": self.get_LineEdit_parts(self.ui.le_selection_pic_columns),
            "marker": self.ui.marker_selection.text(),
            "do_search": self.ui.search.isChecked(),
            "videos_columns_search": self.get_LineEdit_parts(self.ui.le_search_vid_columns),
            "picture_columns_search": self.get_LineEdit_parts(self.ui.le_search_pic_columns),
            "keywords": self.get_LineEdit_parts(self.ui.marker_search),
            "rating_search": self.ui.sb_rating_search.value(),
            "create_picture_folder": self.ui.pictures_2.isChecked(),
            "rating_pictures": self.ui.sp_rating_picturefolder_2.value(),
        }
        return UtilTabInput(**data)

    # ##### FileDialogs ##### #
    def show_filedialog_harddrive_path(self):
        """Handles selecting the harddrive path/folder through a FileDialog"""
        directory = QFileDialog.getExistingDirectory(parent=self, caption="Open dir", directory="")
        if directory:
            self.ui.drop_harddrive.setText(directory)

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
            if self.ui.drop_util_excelfile.text() == "":
                raise ValueError("Bitte gib eine Excel-Datei an.")
            path = Path(self.ui.drop_util_excelfile.text())
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
            traceback.print_exc()
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
