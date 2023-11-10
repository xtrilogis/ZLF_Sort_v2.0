"""Start der App"""
# print("Python Code Starting")
import traceback
from datetime import datetime
from PyQt5.QtCore import *
from pathlib import Path

from pydantic import ValidationError

from assethandling.asset_manager import settings
from assethandling.basemodels import UtilTabInput, RawTabInput, FolderTabInput, ExcelInputOptions, ExcelInput
from ui import Worker
from runner import runners


print("Imports done")

ROOT = "../TestDateien"
ROOT_absolute = "D:/Users/Wisdom/Lernen/Coding_Python/ZLF_Sort_v2.0/TestDateien"
root = Path(ROOT_absolute)
path_raw = "D:/Users/Wisdom/Lernen/Coding_Python/ZLF_Sort_v2.0/TestDateien/Rohmaterial"
pfad_excel = "D:/Users/Wisdom/Lernen/Coding_Python/ZLF_Sort_v2.0/TestDateien/Rohmaterial/Zeltlagerfilm 2022.xlsx"


data_raw = {
    "do_structure": False,
    "do_rename": False,
    "fill_excel": False,
    "create_picture_folder": False,
    "raw_material_folder": root / "Rohmaterial",  # TODO good??
    "first_folder_date": datetime(2023, 7, 26),
    "excel_full_filepath": root / f"Zeltlagerfilm {datetime.now().date().year}.xlsx",
    "custom_path": False,
    "picture_folder": root,
    "excel_folder": root,
    "video_columns": settings["standard-video-columns"],
    "picture_columns": settings["standard-picture-columns"],
    "excel_file_name": f"Zeltlagerfilm {datetime.now().date().year}.xlsx",
    "excel_option": ExcelInputOptions.STANDARD
}


def get_util_input() -> UtilTabInput:
    if path_raw == "" or pfad_excel == "":
        raise ValueError("Bitte fülle die Felder in 'Input' aus")
    data = {
        "raw_material_folder": Path(path_raw),
        "excel_full_filepath": Path(pfad_excel),
        "do_sections": False,
        "do_video_sections": False,
        "do_picture_sections": False,
        "rating_section": 4,
        "do_selections": False,
        "videos_columns_selection": ["Outtakes"],
        "picture_columns_selection": ["Outtakes", "Webseite", "Fotowand"],
        "marker": "x",
        "do_search": False,
        "videos_columns_search": [],
        "picture_columns_search": ["Outtakes", "Webseite", "Fotowand"],
        "keywords": ["x"],
        "rating_search": 4,
        "create_picture_folder": False,
        "rating_pictures": 4,
    }
    return UtilTabInput(**data)


class Main:
    """Class handels UI interaction and input."""
    def __init__(self):
        self.threadpool = QThreadPool()
        self.current_function = None

    def setup_button_connections(self):
        pass

    # ##### BUTTONS "Ordner erstellt" ##### #
    def run_fs(self):
        self.run_folder_setup(function=runners.run_folder_setup)

    # ##### BUTTONS "Rohmaterial verarbeiten" ##### #
    def run_process_raw_full(self):
        self.raw_with_excel(function=runners.run_process_raw_full)

    def run_correct_folder_structure(self):
        self.run_raw_action(function=runners.run_correct_structure)

    def run_rename_files(self):
        self.run_raw_action(function=runners.run_rename_files)

    def create_excel(self):
        self.raw_with_excel(function=runners.create_excel)

    def run_fill_excel(self):
        self.raw_with_excel(function=runners.run_fill_excel)

    def run_create_picture_folder(self):
        self.run_raw_action(function=runners.run_create_picture_folder)

    # ##### BUTTONS "Auswertung" ##### #

    def run_copy_section(self):
        self.run_util_action(function=runners.run_copy_sections)

    def run_copy_selection(self):
        self.run_util_action(function=runners.run_copy_selection)

    def run_search(self):
        self.run_util_action(function=runners.run_search)

    def run_rated_pf(self):
        self.run_util_action(function=runners.run_create_rated_picture_folder)

    def run_util_full(self):
        self.run_util_action(function=runners.run_process_util_full)

    def run_statistic(self):
        self.run_util_action(function=runners.run_statistics)

    @pyqtSlot(str)
    def write_process(self, msg: str):
        """Writes the latest status message to the print label."""
        print(msg)

    @pyqtSlot(str)
    def open_problem_input(self, error: str):
        """Opens a message box displaying a given error"""
        print("------------------------")
        print("Problem:")
        print(error)

    @pyqtSlot()
    def open_excel_exists(self):
        """Opens a message box displaying a given error"""
        print("Die angegebene Excel-Datei existiert bereits.")
        override = input("Soll die Excel überschrieben werden? y/n")
        if "y" in override.lower():
            self.handle_excel_choice("Überschreiben")
        else:
            print("Abbruch")

    def handle_excel_choice(self, i):
        if "Überschreiben" in i:
            self.raw_with_excel(function=self.current_function, override=True)

    @pyqtSlot()
    def process_finished(self):
        print("-------------")
        print("Done")

    # ##### Actions ##### #
    def run_folder_setup(self, function):
        try:
            drop_harddrive = ""  # Todo
            date = datetime(2023, 7, 27)
            if drop_harddrive == "":
                self.open_problem_input(error="Bitte gib einen Dateipfad an.")
                return
            data = FolderTabInput(
                folder=Path(drop_harddrive),
                date=date
            )
        except ValidationError as e:
            traceback.print_exc()
            self.open_problem_input(msg=str(e))
            return
        self.run_action(function=function, slot=self.write_process, input_=data)

    def run_raw_action(self, function):
        try:
            self.current_function = function
            data: RawTabInput = self.get_raw_input()
        except (ValidationError, ValueError) as e:
            traceback.print_exc()
            self.open_problem_input(error=str(e))
            return
        self.current_function = None
        self.run_action(function=function, slot=self.write_process, input_=data)

    def raw_with_excel(self, function, override=False):
        try:
            self.current_function = function
            data: RawTabInput = self.get_raw_input(self.excel(override=override))
        except (ValidationError, ValueError) as e:
            traceback.print_exc()
            self.open_problem_input(error=str(e))
            return
        self.current_function = None
        self.run_action(function=function, slot=self.write_process, input_=data)

    def get_raw_input(self, excel=None) -> RawTabInput:
        data = {
            "do_structure": data_raw["do_structure"],
            "do_rename": data_raw["do_rename"],
            "fill_excel": data_raw["fill_excel"],
            "create_picture_folder": data_raw["create_picture_folder"],
            "raw_material_folder": data_raw["raw_material_folder"],
            "first_folder_date": data_raw["first_folder_date"],
            "excel": excel,
        }
        if data_raw["custom_path"]:
            if data_raw["picture_folder"] == "":
                raise ValueError("Bitte gib einen Speicherort für den Bilderordner an.")
            data["picture_folder"] = Path(data_raw["picture_folder"])
        else:
            data["picture_folder"] = data.get("raw_material_folder").parent / "Bilderordner"

        return RawTabInput(**data)

    def excel(self, override) -> Path | ExcelInput | None:
        if not data_raw["fill_excel"]:
            return None
        excel_option: ExcelInputOptions = data_raw["excel_option"]
        if excel_option == ExcelInputOptions.EXISTING:
            return Path(data_raw["excel_full_filepath"])
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
        if option != ExcelInputOptions.STANDARD and option != ExcelInputOptions.MANUAL:
            error = "Interner Fehler, der Button 'Excel erstellen'\n" \
                    "sollte nicht klickbar sein mit der Option \n" \
                    "vorhandene Excel nutzen. Neustarten."
            raise ValueError(error)
        elif data_raw["raw_material_folder"] == "":
            error = "Bitte gib einen Speicherort für die Excel-Datei an.\n" \
                    "Dazu kannst du bei 'Excel-Datei' einen Ordner \n" \
                    "angeben oder für den Standardweg den Rohmaterialorder \nangeben." \
                    "Für Standards schau dir doch gerne die Anleitung an."
            raise ValueError(error)
        else:
            if option == ExcelInputOptions.MANUAL:
                config = ExcelInput(
                    excel_folder=Path(data_raw["excel_folder"]),
                    excel_file_name=data_raw["excel_file_name"],
                    video_columns=data_raw["video_columns"],
                    picture_columns=data_raw["picture_columns"]
                )
            else:
                config = ExcelInput(
                    excel_folder=Path(data_raw["raw_material_folder"])
                )
            return config

    def run_util_action(self, function):
        try:
            data: UtilTabInput = get_util_input()
        except (ValidationError, ValueError) as e:
            traceback.print_exc()
            self.open_problem_input(error=str(e))
            return
        self.run_action(function=function, slot=self.write_process, input_=data)

    def run_action(self, function, slot, input_):
        worker = Worker(function, inputs=input_)
        worker.signals.new_message.connect(slot)
        worker.signals.problem_with_input.connect(self.open_problem_input)
        worker.signals.finished.connect(self.process_finished)

        # self.threadpool.start(worker)
        worker.run()


if __name__ == "__main__":
    print("")
