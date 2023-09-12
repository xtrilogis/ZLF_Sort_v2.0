"""Start der App"""
# print("Python Code Starting")
from PyQt5.QtWidgets import QApplication, QPlainTextEdit
import sys

from assets import constants
from excel import excelmethods
from inputhandling import validation
from ui.first_draft import Ui_MainWindow
from datetime import datetime
from pathlib import Path
from typing import List
from pydantic import ValidationError

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLineEdit, QDialog
from PyQt5.QtCore import QThread, pyqtSlot, QDate

from assethandling.asset_manager import settings
from assethandling.basemodels import ExcelOptions, FolderTabInput, RawTabStandardInput, UtilTabInput, ExcelConfig, \
    ExcelInput
from ui.dialogs.selection_dialog import SelectionDialog
from ui.thread_worker import Worker
from ui.popups import messageboxes

print("Imports done")


class MainWindow(QMainWindow):
    """Class handels UI interaction and input."""
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow(self)
        self.thread = QThread()
        self.worker = Worker()
        self.setup_ui()
        self.setup_thread_connections()
        self.setup_button_connections()

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

    def setup_thread_connections(self):
        self.worker.moveToThread(self.thread)

        # Signal & Slot connections
        self.worker.new_message_setup.connect(self.write_process_setup)
        self.worker.problem_with_input.connect(self.open_problem_input)
        self.worker.process_finished.connect(self.process_finished)

        self.worker.new_message_raw.connect(self.write_process_raw)
        self.worker.excel_exits_error.connect(self.open_excel_exists)

        self.worker.new_message_excel.connect(self.write_process_util)
        self.thread.start()

    def setup_button_connections(self):
        # ##### BUTTONS "Ordner erstellt" ##### #
        self.ui.harddrive_tb_2.clicked.connect(self.show_filedialog_harddrive_path)
        self.ui.folder_start_pb_2.clicked.connect(self.setup_folder_structure_new)

        # ##### BUTTONS "Rohmaterial verarbeiten" ##### #
        self.ui.rawpath_folder_tb_2.clicked.connect(
            lambda: self.show_filedialog_raw_material_path(self.ui.rawpath_drop_2))
        self.ui.execute_raw_pB.clicked.connect(self.process_raw_full)

        self.ui.correct_fs.clicked.connect(self.correct_structure)
        self.ui.pushButton_7.clicked.connect(self.rename_files)

        # ### Excel File
        self.ui.create_excel_pb.clicked.connect(self.create_excel_file)
        self.ui.fill_excel_pb.clicked.connect(self.fill_excel)

        self.ui.vid_sugestions_pb.clicked.connect(
            lambda: self.show_suggestions(text_edit=self.ui.vid_columns,
                                          suggestions=settings["suggestions-video-columns"])
        )
        self.ui.pic_sugestions_pb.clicked.connect(
            lambda: self.show_suggestions(text_edit=self.ui.pic_columns,
                                          suggestions=settings["suggestions-picture-columns"])
        )
        self.ui.rawpath_folder_tb_4.clicked.connect(
            lambda: self.show_filedialog_raw_material_path(self.ui.excel_folder_drop_4)
        )
        self.ui.excelpath_folder_tb_2.clicked.connect(
            lambda: self.show_filedialog_excel_file_path(self.ui.excelpath_drop_2)
        )
        self.ui.picture_tb.clicked.connect(
            lambda: self.show_filedialog_raw_material_path(self.ui.picture_drop)
        )
        self.ui.create_picture_folder_pb.clicked.connect(self.create_picture_folder)

        # ##### BUTTONS "Auswertung" ##### #
        self.ui.rawpath_folder_tb_3.clicked.connect(
            lambda: self.show_filedialog_raw_material_path(self.ui.rawpath_drop_3)
        )
        self.ui.excelpath_folder_tb_3.clicked.connect(
            lambda: self.show_filedialog_excel_file_path(self.ui.excelpath_drop_3)
        )
        self.ui.excel_start_pb_6.clicked.connect(self.create_sections)
        self.ui.excel_start_pb_7.clicked.connect(self.create_selections)
        self.ui.excel_start_pb_4.clicked.connect(self.search_excel)
        self.ui.excel_start_pb_8.clicked.connect(self.create_rated_picture_folder)
        self.ui.pushButton_5.clicked.connect(self.process_util_full)
        self.ui.pushButton_6.clicked.connect(self.create_statistics)

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

    # ##### PyQt Slots ##### #
    @pyqtSlot(str)
    def write_process_setup(self, msg):
        """Writes the latest status message to the print label."""
        self.ui.print_label_setup.setText(msg)

    @pyqtSlot(str)
    def write_process_raw(self, msg):
        self.ui.print_label.setText(msg)

    @pyqtSlot(str)
    def write_process_util(self, msg):
        text = self.ui.print_label_2.text()
        self.ui.print_label_2.setText(f"{text}\n{msg}")

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
        try:
            if self.ui.harddrive_drop_2.text() == "":
                self.open_problem_input(msg="Bitte gib einen Dateipfad an.")
            else:
                data = FolderTabInput(
                    folder=Path(self.ui.harddrive_drop_2.text()),
                    date=self.ui.dateEdit.date().toPyDate()
                )
                self.worker.setup_folder_structure(inputs=data)
        except ValidationError as e:
            self.open_problem_input(msg=str(e))

    # ##### PART II: Raw Material / 'Rohmaterial verarbeiten' ##### #
    # ### Button Methods ### #
    def process_raw_full(self):
        # TODO implementation
        try:
            data = self.get_raw_inputs()
            print(data.model_dump_json(indent=4))
        except ValidationError as e:
            self.open_problem_input(error=str(e))
        except ValueError as e:
            self.open_problem_input(error=str(e))

    def correct_structure(self):
        # TODO implementation
        # get input
        # self.worker.correct_file_structure(path="")
        pass

    def rename_files(self):
        # TODO implementations
        pass

    def create_excel_file(self, override=False):
        # TODO Testing
        text = self.ui.comboBox.currentText()
        if text != ExcelOptions.STANDARD.value or text != ExcelOptions.MANUAL.value:
            error = "Interner Fehler, der Button 'Excel erstellen'\n" \
                    "sollte nicht klickbar sein mit der Option \n" \
                    "vorhandene Excel nutzen. Neustarten."
            self.open_problem_input(error=error)
        elif self.ui.excel_folder_drop_4.text() == "":
            error = "Bitte gib einen Speicherort für die Excel-Datei an.\n" \
                    "Dazu kannst du bei 'Excel-Datei' einen Ordner \n" \
                    "angeben oder für den Standardweg den Rohmaterialorder \nangeben." \
                    "Für Standards schau dir doch gerne die Anleitung an."
            self.open_problem_input(error=error)
        else:
            if text == ExcelOptions.MANUAL.value:
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
            self.worker.create_excel(conf=config, override=override)

    def handle_excel_choice(self, i):
        if "Überschreiben" in i.text():
            self.create_excel_file(override=True)

    def fill_excel(self):
        # TODO implementation
        # self.worker.fill_excel()
        # if mode == existing nur auslesen sonst, raw mat input
        pass

    def create_picture_folder(self):
        # TODO implementation
        # lambda: self.worker.create_picture_folder()  # TODO
        pass

    def show_suggestions(self, text_edit: QPlainTextEdit, suggestions: List[str]):
        dial = SelectionDialog("Spaltenvorschläge", "Spalten", suggestions, self)
        if dial.exec_() == QDialog.Accepted:
            select: List[str] = dial.itemsSelected()
            previous_columns: List[str] = self.get_PlainTextEdit_parts(text_edit)
            previous_columns.extend(select)
            text = ", ".join(previous_columns)
            text_edit.setPlainText(text)

    # ### Helper Methods ### #
    def get_excel_config(self) -> ExcelConfig:
        data = {}

        return ExcelConfig(**data)

    def get_raw_inputs(self):
        # Optional inputs like picture_folder besser handle
        if self.ui.rawpath_drop_2.text() == "":  # außer bei create excel
            raise ValueError("Bitte gib den Pfad zum Rohmaterialordner an.")
        excel_option: ExcelOptions = ExcelOptions(self.ui.comboBox.currentText())
        data = {
            "do_structure": self.ui.structur_cB.isChecked(),
            "do_rename": self.ui.rename_cB.isChecked(),
            "fill_excel": self.ui.fill_excel_cB.isChecked(),
            "create_picture_folder": self.ui.diashow_cB.isChecked(),
            "raw_material_folder": Path(self.ui.rawpath_drop_2.text()),
            "excel_option": excel_option,
            "excel_full_filepath": None
        }
        if excel_option == ExcelOptions.EXISTING:
            data['excel_full_filepath'] = Path(self.ui.excelpath_drop_2.text())
            data["excel_folder"] = data.get('excel_full_filepath').parent
        elif excel_option == ExcelOptions.MANUAL:
            if self.ui.excel_folder_drop_4.text() == "":
                raise ValueError("Bitte gib einen Speicherort für die Excel-Datei an.")
            data["excel_folder"]: Path = Path(self.ui.excel_folder_drop_4.text())
            data["excel_file_name"]: str = self.ui.lineEdit.text()
            data["video_columns"]: List[str] = self.get_LineEdit_parts(self.ui.vid_columns)
            data["picture_columns"]: List[str] = self.get_LineEdit_parts(self.ui.pic_columns)
        else:
            data["excel_folder"]: Path = data["raw_material_folder"].parent

        if self.ui.groupBox_2.isChecked():
            if self.ui.picture_drop.text() == "":
                raise ValueError("Bitte gib einen Speicherort für den Bilderordner an.")
            data["picture_folder"] = Path(self.ui.picture_drop.text())
        else:
            data["picture_folder"] = data["raw_material_folder"].parent

        info = RawTabStandardInput(**data)
        if info.excel_full_filepath is None:
            info.excel_full_filepath = info.excel_folder / info.excel_file_name
        return info

    # ##### PART III: Util / '' ##### #
    def create_sections(self):
        try:
            data: UtilTabInput = self.get_util_input()
            self.worker.run_copy_sections(inputs=data)
        except (ValidationError, ValueError) as e:
            self.open_problem_input(error=str(e))

    def create_selections(self):
        try:
            data: UtilTabInput = self.get_util_input()
            self.worker.run_selection(inputs=data)
        except (ValidationError, ValueError) as e:
            self.open_problem_input(error=str(e))

    def search_excel(self):
        try:
            data: UtilTabInput = self.get_util_input()
            self.worker.run_search(inputs=data)
        except (ValidationError, ValueError) as e:
            self.open_problem_input(error=str(e))

    def create_rated_picture_folder(self):
        try:
            data: UtilTabInput = self.get_util_input()
            self.worker.run_copy_picture_folder(inputs=data)
        except (ValidationError, ValueError) as e:
            self.open_problem_input(error=str(e))

    def process_util_full(self):
        try:
            data: UtilTabInput = self.get_util_input()
            self.worker.full_util_tab(inputs=data)
        except (ValidationError, ValueError) as e:
            self.open_problem_input(error=str(e))

    def create_statistics(self):
        try:
            data: UtilTabInput = self.get_util_input()
            self.worker.run_statistics(raw_path=data.raw_material_folder)
        except (ValidationError, ValueError) as e:
            self.open_problem_input(error=str(e))

    def select_columns(self, line_edit: QLineEdit, sheet: str):
        try:
            if self.ui.excelpath_drop_3.text() == "":
                raise ValueError("Bitte gib eine Excel-Datei an.")
            path = Path(self.ui.excelpath_drop_3.text())
            errors = validation.validate_excel_file(excel_file=path)
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
