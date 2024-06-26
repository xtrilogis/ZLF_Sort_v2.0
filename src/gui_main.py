"""Start der App"""
print("Python Code Starting")
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import List

from pydantic import ValidationError
from PyQt5 import QtGui
from PyQt5.QtCore import QDate, QMutex, Qt, QThreadPool, QWaitCondition, pyqtSlot
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
)

from assethandling.asset_manager import gif, settings
from assethandling.basemodels import (
    ExcelInput,
    ExcelInputOptions,
    ExcelOption,
    FolderTabInput,
    RawTabInput,
    UtilTabInput,
)
from excel import excelmethods
from inputhandling.validation import validate_excel_file
from runner import runners
from threadworker.thread_worker import Worker
from ui import SelectionDialog, Ui_MainWindow, messageboxes

print("Imports done")


class MainWindow(QMainWindow):
    """Class handels UI interaction and input."""

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow(self)
        self.setup_ui()
        self.setup_input_buttons()
        self.setup_executions_buttons()

        self.mutex = QMutex()
        self.cond = QWaitCondition()
        self.threadpool = QThreadPool()

        self.current_function = None

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
        self.ui.pic_columns.setPlainText(
            ", ".join(settings["standard-picture-columns"])
        )
        self.ui.le_excel_file_name.setText(
            f"Zeltlagerfilm {datetime.now().date().year}.xlsx"
        )

        self.setup_responsive_styles()
        self.setup_gif()

    def setup_gif(self):
        self.movie = QtGui.QMovie(gif)
        self.ui.process_gif_label.setMaximumSize(55, 26)
        self.ui.process_gif_label_2.setMaximumSize(55, 26)
        self.ui.process_gif_label.setMovie(self.movie)
        self.ui.process_gif_label_2.setMovie(self.movie)
        self.movie.start()
        self.movie.stop()

    def show_frame(self):
        text = self.ui.excel_option.currentText()
        if text == ExcelInputOptions.STANDARD.value:
            self.ui.help_standard_excel.show()
            self.ui.excel_path.hide()
            self.ui.manuel_columns.hide()
            self.ui.frame_8.show()
            self.ui.pb_create_excel.show()
            self.ui.pb_fill_excel.setText("Excel erstellen und Dateien eintragen")
        elif text == ExcelInputOptions.EXISTING.value:
            self.ui.help_standard_excel.hide()
            self.ui.excel_path.show()
            self.ui.manuel_columns.hide()
            self.ui.frame_8.hide()
            self.ui.pb_create_excel.hide()
            self.ui.pb_fill_excel.setText("Dateien eintragen")
        else:
            self.ui.excel_path.hide()
            self.ui.manuel_columns.show()
            self.ui.help_standard_excel.hide()
            self.ui.frame_8.show()
            self.ui.pb_create_excel.show()
            self.ui.pb_fill_excel.setText("Excel erstellen und Dateien eintragen")

    def setup_responsive_styles(self):
        self.ui.drop_util_excelfile.setStyleSheet("QLineEdit { color: 'red';}")
        self.ui.drop_util_rawpath.setStyleSheet("QLineEdit { color: 'red';}")
        self.ui.drop_raw_rawpath.setStyleSheet("QLineEdit { color: 'red';}")
        self.ui.drop_raw_excel_file.setStyleSheet("QLineEdit { color: 'red';}")
        self.ui.drop_picture_folder.setStyleSheet("QLineEdit { color: 'red';}")
        self.ui.drop_harddrive.setStyleSheet("QLineEdit { color: 'red';}")

        self.ui.drop_util_excelfile.textChanged.connect(
            lambda text: self.ui.drop_util_excelfile.setStyleSheet(
                "QLineEdit { color: %s}" % ("green" if text else "red")
            )
        )
        self.ui.drop_util_rawpath.textChanged.connect(
            lambda text: self.ui.drop_util_rawpath.setStyleSheet(
                "QLineEdit { color: %s}" % ("green" if text else "red")
            )
        )
        self.ui.drop_raw_rawpath.textChanged.connect(
            lambda text: self.ui.drop_raw_rawpath.setStyleSheet(
                "QLineEdit { color: %s}" % ("green" if text else "red")
            )
        )
        self.ui.drop_raw_excel_file.textChanged.connect(
            lambda text: self.ui.drop_raw_excel_file.setStyleSheet(
                "QLineEdit { color: %s}" % ("green" if text else "red")
            )
        )
        self.ui.drop_picture_folder.textChanged.connect(
            lambda text: self.ui.drop_picture_folder.setStyleSheet(
                "QLineEdit { color: %s}" % ("green" if text else "red")
            )
        )
        self.ui.drop_harddrive.textChanged.connect(
            lambda text: self.ui.drop_harddrive.setStyleSheet(
                "QLineEdit { color: %s}" % ("green" if text else "red")
            )
        )

        self.ui.cb_segment_videos.clicked.connect(self.util_buttons_status)
        self.ui.cb_segment_picture.clicked.connect(self.util_buttons_status)

        self.ui.le_selection_pic_columns.textChanged.connect(self.util_buttons_status)
        self.ui.le_selection_vid_columns.textChanged.connect(self.util_buttons_status)
        self.ui.marker_selection.textChanged.connect(self.util_buttons_status)

        self.ui.le_search_pic_columns.textChanged.connect(self.util_buttons_status)
        self.ui.le_search_vid_columns.textChanged.connect(self.util_buttons_status)
        self.ui.marker_search.textChanged.connect(self.util_buttons_status)

        self.util_buttons_status()

    def util_buttons_status(self):
        self.ui.pb_section.setEnabled(
            self.ui.cb_segment_videos.isChecked()
            or self.ui.cb_segment_picture.isChecked()
        )
        self.ui.pb_start_selection.setEnabled(
            bool(self.ui.marker_selection.text())
            and (
                bool(self.ui.le_selection_vid_columns.text())
                or bool(self.ui.le_selection_pic_columns.text())
            )
        )
        self.ui.pb_search.setEnabled(
            bool(self.ui.marker_search.text())
            and (
                bool(self.ui.le_search_pic_columns.text())
                or bool(self.ui.le_search_vid_columns.text())
            )
        )

    def setup_input_buttons(self):
        # ##### BUTTONS "Ordner erstellt" ##### #
        self.ui.tb_harddrive.clicked.connect(self.show_filedialog_harddrive_path)
        # ##### BUTTONS "Rohmaterial verarbeiten" ##### #
        self.ui.tb_raw_rawpath.clicked.connect(
            lambda: self.show_filedialog_folder(self.ui.drop_raw_rawpath)
        )
        self.ui.pb_vid_sugestions.clicked.connect(
            lambda: self.show_suggestions(
                text_edit=self.ui.vid_columns,
                suggestions=settings["suggestions-video-columns"],
            )
        )
        self.ui.pb_pic_sugestions.clicked.connect(
            lambda: self.show_suggestions(
                text_edit=self.ui.pic_columns,
                suggestions=settings["suggestions-picture-columns"],
            )
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
        # ##### BUTTONS "Auswertung" ##### #
        self.ui.tb_util_rawpath.clicked.connect(
            lambda: self.show_filedialog_folder(self.ui.drop_util_rawpath)
        )
        self.ui.tb_util_excelfile.clicked.connect(
            lambda: self.show_filedialog_excel_file_path(self.ui.drop_util_excelfile)
        )
        self.ui.pb_select_pic_columns.clicked.connect(
            lambda: self.select_columns(
                line_edit=self.ui.le_selection_pic_columns, sheet="Bilder"
            )
        )
        self.ui.pb_select_vid_columns.clicked.connect(
            lambda: self.select_columns(
                line_edit=self.ui.le_selection_vid_columns, sheet="Videos"
            )
        )
        self.ui.pb_search_pic_columns.clicked.connect(
            lambda: self.select_columns(
                line_edit=self.ui.le_search_pic_columns, sheet="Bilder"
            )
        )
        self.ui.pb_search_vid_columns.clicked.connect(
            lambda: self.select_columns(
                line_edit=self.ui.le_search_vid_columns, sheet="Videos"
            )
        )

    def setup_executions_buttons(self):
        # ##### BUTTONS "Ordner erstellt" ##### #
        self.ui.pb_foldersetup.clicked.connect(
            lambda: self.run_folder_setup(function=runners.run_folder_setup)
        )

        # ##### BUTTONS "Rohmaterial verarbeiten" ##### #
        self.ui.pb_start_raw_full.clicked.connect(
            lambda: self.run_raw_action(function=runners.run_process_raw_full)
        )
        self.ui.pb_correct_fs.clicked.connect(
            lambda: self.run_raw_action(function=runners.run_correct_structure)
        )
        self.ui.pb_rename.clicked.connect(
            lambda: self.run_raw_action(function=runners.run_rename_files)
        )
        self.ui.pb_create_excel.clicked.connect(
            lambda: self.run_raw_action(function=runners.run_create_excel)
        )
        self.ui.pb_fill_excel.clicked.connect(
            lambda: self.run_raw_action(function=runners.run_fill_excel)
        )
        self.ui.pb_create_picture_folder.clicked.connect(
            lambda: self.run_raw_action(function=runners.run_create_picture_folder)
        )

        # ##### BUTTONS "Auswertung" ##### #
        self.ui.pb_section.clicked.connect(
            lambda: self.run_util_action(function=runners.run_copy_sections)
        )
        self.ui.pb_start_selection.clicked.connect(
            lambda: self.run_util_action(function=runners.run_copy_selection)
        )
        self.ui.pb_search.clicked.connect(
            lambda: self.run_util_action(function=runners.run_search)
        )
        self.ui.pb_picturefolder.clicked.connect(
            lambda: self.run_util_action(
                function=runners.run_create_rated_picture_folder
            )
        )
        self.ui.pb_util_all.clicked.connect(
            lambda: self.run_util_action(function=runners.run_process_util_full)
        )
        self.ui.pb_statistic.clicked.connect(
            lambda: self.run_util_action(function=runners.run_statistics)
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

        self.util_buttons_status()

    @staticmethod
    def add_label_text(msg, label: QLabel):
        text = label.text()
        label.setText(f"{text}\n{msg}".strip())

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
        msg.setTextInteractionFlags(Qt.TextSelectableByMouse)
        msg.exec()

    @pyqtSlot(str)
    def open_information_input(self, text: str):
        answer, ok = QInputDialog().getItem(self, "Eingabe", text, ["Ja", "Nein"])
        if ok and answer:
            self.sender().data_response.emit(answer)
        self.cond.wakeAll()

    @pyqtSlot()
    def process_finished(self):
        self.enable_work_buttons()
        self.movie.stop()

    # ##### Actions ##### #
    def get_folder_input(self) -> FolderTabInput:
        if self.ui.drop_harddrive.text() == "":
            raise ValueError("Bitte gib einen Dateipfad an.")
        return FolderTabInput(
            folder=Path(self.ui.drop_harddrive.text()),
            date=self.ui.date_lkw.date().toPyDate(),
        )

    def run_folder_setup(self, function):
        try:
            data: FolderTabInput = self.get_folder_input()
        except (ValidationError, ValueError) as e:
            traceback.print_exc()
            self.open_problem_input(error=str(e))
            return
        self.run_action(function=function, slot=self.write_process_setup, input_=data)

    def get_raw_input(self) -> RawTabInput:
        data = {
            "do_rename": self.ui.cb_rename.isChecked(),
            "fill_excel": self.ui.cb_fill_excel.isChecked(),
            "create_picture_folder": self.ui.cb_diashow.isChecked(),
            "raw_material_folder": Path(self.ui.drop_raw_rawpath.text()),
            "first_folder_date": self.ui.date_correct_fs.date().toPyDate(),
            "excel": self._get_excel_input(),
        }
        data["picture_folder"] = self._get_picture_folder(data["raw_material_folder"])
        return RawTabInput(**data)

    def _get_excel_input(self) -> ExcelInput:
        excel_input_option: ExcelInputOptions = ExcelInputOptions(
            self.ui.excel_option.currentText()
        )
        if excel_input_option == ExcelInputOptions.EXISTING:
            filepath: Path = Path(self.ui.drop_raw_excel_file.text())
            data = {
                "option": ExcelOption.EXISTING,
                "name": filepath.name,
                "folder": filepath.parent,
                "video_columns": [],  # use default value instead?
                "picture_columns": [],
            }
        elif excel_input_option == ExcelInputOptions.MANUAL:
            data = {
                "option": ExcelOption.CREATE,
                "name": self.ui.le_excel_file_name.text(),
                "folder": Path(self.ui.drop_excel_folder.text()),
                "video_columns": self.get_PlainTextEdit_parts(self.ui.vid_columns),
                "picture_columns": self.get_PlainTextEdit_parts(self.ui.pic_columns),
            }
        else:
            data = {
                "option": ExcelOption.CREATE,
                "folder": Path(self.ui.drop_raw_rawpath.text()).parent,
            }
        return ExcelInput(**data)

    def _get_picture_folder(self, raw_material_folder: Path):
        if self.ui.custom_picture_folder.isChecked():
            if self.ui.drop_picture_folder.text() == "":
                raise ValueError("Bitte gib einen Speicherort für den Bilderordner an.")
            return Path(self.ui.drop_picture_folder.text())
        return raw_material_folder.parent / "Bilderordner"

    def run_raw_action(self, function):
        try:
            data: RawTabInput = self.get_raw_input()
        except (ValidationError, ValueError) as e:
            traceback.print_exc()
            self.open_problem_input(error=str(e))
            return
        self.run_action(function=function, slot=self.write_process_raw, input_=data)

    def run_util_action(self, function):
        try:
            data: UtilTabInput = self.get_util_input()
        except (ValidationError, ValueError) as e:
            traceback.print_exc()
            self.open_problem_input(error=str(e))
            return
        self.run_action(function=function, slot=self.write_process_util, input_=data)

    def get_util_input(self) -> UtilTabInput:
        if (
            self.ui.drop_util_rawpath.text() == ""
            or self.ui.drop_util_excelfile.text() == ""
        ):
            raise ValueError("Bitte fülle die Felder in 'Input' aus")
        data = {
            "raw_material_folder": Path(self.ui.drop_util_rawpath.text()),
            "excel_full_filepath": Path(self.ui.drop_util_excelfile.text()),
            "do_sections": self.ui.section.isChecked(),
            "do_video_sections": self.ui.cb_segment_videos.isChecked(),
            "do_picture_sections": self.ui.cb_segment_picture.isChecked(),
            "rating_section": self.ui.sb_rating_section.value(),
            "do_selections": self.ui.selection.isChecked(),
            "videos_columns_selection": self.get_LineEdit_parts(
                self.ui.le_selection_vid_columns
            ),
            "picture_columns_selection": self.get_LineEdit_parts(
                self.ui.le_selection_pic_columns
            ),
            "marker": self.ui.marker_selection.text(),
            "do_search": self.ui.search.isChecked(),
            "videos_columns_search": self.get_LineEdit_parts(
                self.ui.le_search_vid_columns
            ),
            "picture_columns_search": self.get_LineEdit_parts(
                self.ui.le_search_pic_columns
            ),
            "keywords": self.get_LineEdit_parts(self.ui.marker_search),
            "rating_search": self.ui.sb_rating_search.value(),
            "create_picture_folder": self.ui.pictures_2.isChecked(),
            "rating_pictures": self.ui.sp_rating_picturefolder_2.value(),
        }
        return UtilTabInput(**data)

    def run_action(self, function, slot, input_):
        self.disable_work_buttons()
        self.movie.start()
        worker = Worker(function, self.mutex, self.cond, inputs=input_)
        worker.signals.new_message.connect(slot)
        worker.signals.problem_with_input.connect(self.open_problem_input)
        worker.signals.finished.connect(self.process_finished)
        worker.signals.request_data.connect(self.open_information_input)

        self.threadpool.start(worker)

    # ##### FileDialogs ##### #
    def show_filedialog_harddrive_path(self):
        """Handles selecting the harddrive path/folder through a FileDialog"""
        directory = QFileDialog.getExistingDirectory(
            parent=self, caption="Open dir", directory=""
        )
        if directory:
            self.ui.drop_harddrive.setText(directory)

    def show_filedialog_folder(self, line_edit: QLineEdit):
        """Handles selecting the raw material path/folder through a FileDialog"""
        directory = QFileDialog.getExistingDirectory(
            parent=self, caption="Open dir", directory=""
        )
        if directory:
            line_edit.setText(directory)

    def show_filedialog_excel_file_path(self, line_edit: QLineEdit):
        """Handles selecting the Excel file through a FileDialog"""
        directory, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Open Excel",
            directory="",
            filter="Excel-Files (*.xlsx)",
        )
        if directory:
            line_edit.setText(directory)

    # ##### other ##### #
    def select_columns(self, line_edit: QLineEdit, sheet: str):
        try:
            if self.ui.drop_util_excelfile.text() == "":
                raise ValueError("Bitte gib eine Excel-Datei an.")
            path: Path = Path(self.ui.drop_util_excelfile.text())
            validate_excel_file(excel_file=path)
            items: List[str] = excelmethods.get_columns(excel=path, sheet=sheet)
            dial = SelectionDialog("Spalten Auswahl", "Spalten", items, self)
            if dial.exec_() == QDialog.Accepted:
                select: List[str] = dial.itemsSelected()
                text: str = ", ".join(select)
                line_edit.setText(text)
        except Exception as e:
            traceback.print_exc()
            self.open_problem_input(error=str(e))

    @staticmethod
    def get_LineEdit_parts(element: QLineEdit) -> List[str]:
        cols: List[str] = []
        for part in element.text().split(","):
            if part.strip():
                cols.append(part.strip())
        return cols

    @staticmethod
    def get_PlainTextEdit_parts(element: QPlainTextEdit) -> List[str]:
        cols: List[str] = []
        for part in element.document().toRawText().split(","):
            if part.strip():
                cols.append(part.strip())
        return cols


def main(app=QApplication(sys.argv)):
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
