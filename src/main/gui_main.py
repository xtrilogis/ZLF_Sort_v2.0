"""Start der App"""
# print("Python Code Starting")
from datetime import datetime
from typing import List

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

    def setup_ui(self):
        self.ui.tabWidget.setCurrentIndex(0)
        # Setup Start
        self.ui.dateEdit.setDate(QDate.currentDate())
        # setup Raw
        self.ui.tabWidget_raw.setCurrentIndex(0)
        self.show_frame()
        self.ui.comboBox.currentIndexChanged.connect(self.show_frame)
        self.ui.vid_columns.setPlainText(", ".join(settings["standard-video-columns"]))
        self.ui.pic_columns.setPlainText(", ".join(settings["standard-picture-columns"]))
        self.ui.lineEdit.setText(f"Zeltlagerfilm {datetime.now().date().year}.xlsx")

        self.setup_responsive_styles()

    def show_frame(self):
        text = self.ui.comboBox.currentText()
        if text == ExcelOptions.STANDARD.value:
            self.ui.help_standard_excel.show()
            self.ui.excel_path.hide()
            self.ui.manuel_columns.hide()
            self.ui.frame_8.show()
            self.ui.create_excel_pb.show()
        elif text == ExcelOptions.EXISTING.value:
            self.ui.help_standard_excel.hide()
            self.ui.excel_path.show()
            self.ui.manuel_columns.hide()
            self.ui.frame_8.hide()
            self.ui.create_excel_pb.hide()
        else:
            self.ui.excel_path.hide()
            self.ui.manuel_columns.show()
            self.ui.help_standard_excel.hide()
            self.ui.frame_8.show()
            self.ui.create_excel_pb.show()

    def setup_responsive_styles(self):
        # TODO für alle wichtigen Input LineEdits
        self.ui.harddrive_drop_2.textChanged.connect(lambda text: self.ui.harddrive_drop_2.setStyleSheet(
            "QLineEdit { background-color: %s}" % ('green' if text else 'red')))

    def setup_button_connections(self):
        # ##### BUTTONS "Ordner erstellt" ##### #
        self.ui.harddrive_tb_2.clicked.connect(self.show_filedialog_harddrive_path)
        self.ui.folder_start_pb_2.clicked.connect(
            lambda: self.run_folder_setup(function=runners.run_folder_setup))

        # ##### BUTTONS "Rohmaterial verarbeiten" ##### #
        self.ui.rawpath_folder_tb_2.clicked.connect(
            lambda: self.show_filedialog_folder(self.ui.rawpath_drop_2))
        self.ui.execute_raw_pB.clicked.connect(
            lambda: self.run_raw_action(function=runners.run_process_raw_full))
        self.ui.correct_fs.clicked.connect(
            lambda: self.run_raw_action(function=runners.run_correct_structure))
        self.ui.pushButton_7.clicked.connect(
            lambda: self.run_raw_action(function=runners.run_rename_files))

        self.ui.create_excel_pb.clicked.connect(
            lambda: self.run_action(function=runners.create_excel,
                                    slot=self.write_process_raw,
                                    input_=self.excel(False)))
        self.ui.fill_excel_pb.clicked.connect(
            lambda: self.run_raw_action(function=runners.run_fill_excel))

        self.ui.vid_sugestions_pb.clicked.connect(
            lambda: self.show_suggestions(text_edit=self.ui.vid_columns,
                                          suggestions=settings["suggestions-video-columns"])
        )
        self.ui.pic_sugestions_pb.clicked.connect(
            lambda: self.show_suggestions(text_edit=self.ui.pic_columns,
                                          suggestions=settings["suggestions-picture-columns"])
        )
        self.ui.rawpath_folder_tb_4.clicked.connect(
            lambda: self.show_filedialog_folder(self.ui.excel_folder_drop_4)
        )
        self.ui.excelpath_folder_tb_2.clicked.connect(
            lambda: self.show_filedialog_excel_file_path(self.ui.excelpath_drop_2)
        )

        self.ui.picture_tb.clicked.connect(
            lambda: self.show_filedialog_folder(self.ui.picture_drop)
        )
        self.ui.create_picture_folder_pb.clicked.connect(
            lambda: self.run_raw_action(function=runners.run_create_picture_folder)
        )

        # ##### BUTTONS "Auswertung" ##### #
        self.ui.rawpath_folder_tb_3.clicked.connect(
            lambda: self.show_filedialog_folder(self.ui.rawpath_drop_3)
        )
        self.ui.excelpath_folder_tb_3.clicked.connect(
            lambda: self.show_filedialog_excel_file_path(self.ui.excelpath_drop_3)
        )

        self.ui.excel_start_pb_6.clicked.connect(
            lambda: self.run_util_action(function=runners.run_copy_sections))
        self.ui.excel_start_pb_7.clicked.connect(
            lambda: self.run_util_action(function=runners.run_copy_selection))
        self.ui.excel_start_pb_4.clicked.connect(
            lambda: self.run_util_action(function=runners.run_search))
        self.ui.excel_start_pb_8.clicked.connect(
            lambda: self.run_util_action(function=runners.run_create_rated_picture_folder))
        self.ui.pushButton_5.clicked.connect(
            lambda: self.run_util_action(function=runners.run_process_util_full))
        self.ui.pushButton_6.clicked.connect(
            lambda: self.run_util_action(function=runners.run_statistics))

        self.ui.pushButton_3.clicked.connect(
            lambda: self.select_columns(line_edit=self.ui.column_pictures_linee_3, sheet="Bilder")
        )
        self.ui.pushButton_4.clicked.connect(
            lambda: self.select_columns(line_edit=self.ui.column_videos_linee_3, sheet="Videos")
        )
        self.ui.pushButton.clicked.connect(
            lambda: self.select_columns(line_edit=self.ui.column_pictures_linee_2, sheet="Bilder")
        )
        self.ui.pushButton_2.clicked.connect(
            lambda: self.select_columns(line_edit=self.ui.column_videos_linee_2, sheet="Videos")
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

    def handle_excel_choice(self, i):
        if "Überschreiben" in i.text():
            self.run_raw_action(function=self.current_function, override=True)

    @pyqtSlot()
    def process_finished(self):
        self.enable_work_buttons()
        # self.movie.stop()

    # ##### Actions ##### #
    def run_folder_setup(self, function):
        self.disable_work_buttons()
        # self.movie.start()
        try:
            if self.ui.harddrive_drop_2.text() == "":
                self.open_problem_input(msg="Bitte gib einen Dateipfad an.")
                return
            data = FolderTabInput(
                folder=Path(self.ui.harddrive_drop_2.text()),
                date=self.ui.dateEdit.date().toPyDate()
            )
        except ValidationError as e:
            self.open_problem_input(msg=str(e))
            return
        self.run_action(function=function, slot=self.write_process_setup, input_=data)

    def run_raw_action(self, function, override=False):
        try:
            self.current_function = function
            data: RawTabInput = self.get_raw_input(override=override)
        except (ValidationError, ValueError) as e:
            self.open_problem_input(error=str(e))
            return
        self.current_function = None
        self.run_action(function=function, slot=self.write_process_raw, input_=data)

    def get_raw_input(self, override) -> RawTabInput:
        if self.ui.fill_excel_cB.isChecked():
            excel = self.excel(override)

        else:
            excel = Path(".")
        data = {
            "do_structure": self.ui.structur_cB.isChecked(),
            "do_rename": self.ui.rename_cB.isChecked(),
            "fill_excel": self.ui.fill_excel_cB.isChecked(),
            "create_picture_folder": self.ui.diashow_cB.isChecked(),
            "raw_material_folder": Path(self.ui.rawpath_drop_2.text()),
            "first_folder_date": self.ui.dateEdit_2.date().toPyDate(),
            "excel": excel,
        }
        if self.ui.groupBox_2.isChecked():
            if self.ui.picture_drop.text() == "":
                raise ValueError("Bitte gib einen Speicherort für den Bilderordner an.")
            data["picture_folder"] = Path(self.ui.picture_drop.text())
        else:
            data["picture_folder"] = data["raw_material_folder"].parent

        return RawTabInput(**data)

    def excel(self, override) -> Path | ExcelInput:
        excel_option: ExcelOptions = ExcelOptions(self.ui.comboBox.currentText())
        if excel_option == ExcelOptions.EXISTING:
            path = Path(self.ui.excelpath_drop_2.text())
            if path.exists():
                self.open_excel_exists()
        else:
            config = self._get_excel_input(option=excel_option)
            config.override = override
            if (config.excel_folder / config.excel_file_name).exists() and not override:
                self.open_excel_exists()
            return config

    def _get_excel_input(self, option) -> ExcelInput:
        if option != ExcelOptions.STANDARD or option != ExcelOptions.MANUAL:
            error = "Interner Fehler, der Button 'Excel erstellen'\n" \
                    "sollte nicht klickbar sein mit der Option \n" \
                    "vorhandene Excel nutzen. Neustarten."
            raise ValueError(error)
        elif self.ui.excel_folder_drop_4.text() == "":
            error = "Bitte gib einen Speicherort für die Excel-Datei an.\n" \
                    "Dazu kannst du bei 'Excel-Datei' einen Ordner \n" \
                    "angeben oder für den Standardweg den Rohmaterialorder \nangeben." \
                    "Für Standards schau dir doch gerne die Anleitung an."
            raise ValueError(error)
        else:
            if option == ExcelOptions.MANUAL:
                config = ExcelInput(
                    excel_folder=Path(self.ui.excel_folder_drop_4.text()),
                    excel_file_name=self.ui.lineEdit.text(),
                    video_columns=self.ui.vid_columns.text().split(", "),
                    picture_columns=self.ui.pic_columns.text().split(", ")
                )
            else:
                config = ExcelInput(
                    excel_folder=Path(self.ui.excel_folder_drop_4.text())
                )
            return config

    def run_util_action(self, function):
        try:
            data: UtilTabInput = self.get_util_input()
        except (ValidationError, ValueError) as e:
            self.open_problem_input(error=str(e))
            return
        self.run_action(function=function, slot=self.write_process_util, input_=data)

    def run_action(self, function, slot, input_):
        self.disable_work_buttons()
        # self.movie.start()
        worker = Worker(function, inputs=input_)
        worker.signals.new_message.connect(slot)
        worker.signals.problem_with_input.connect(self.open_problem_input)
        worker.signals.finished.connect(self.process_finished)

    def get_util_input(self) -> UtilTabInput:
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
