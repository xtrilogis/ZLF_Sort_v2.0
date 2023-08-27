from datetime import datetime
from typing import List
from pathlib import Path
from PyQt5.QtCore import QDate
from assethandling.basemodels import ExcelOptions, FolderTabInput
from assethandling.asset_manager import settings
from ui import thread_worker as tw
from assethandling import asset_manager

ROOT = "../TestDateien"
ROOT_absolute = "D:/Users/Wisdom/Lernen/Coding_Python/ZLF_Sort_v2.0/TestDateien"


def create_folder_structure():
    worker = tw.Worker()
    data = FolderTabInput(
        folder=Path(ROOT_absolute),
        date=datetime.now()
    )
    worker.setup_folder_structure(inputs=data)


def process_raw_full():
    pass


def create_excel_from_sug():
    pass


def create_standard_excel():
    pass


def process_raw():
    worker = tw.Worker()
    #process_raw_full()

    #worker.correct_file_structure(path="")  # TODO

    # ### Excel File
    # vorhandene Excel einfach übernehmen
    # create excel
    #create_excel_from_sug()  # TODO
    #create_standard_excel()  # TODO
    # path standard Rohmaterial.parent
    worker.create_excel(file_name="test", path=Path(ROOT), option=ExcelOptions.MANUAL)  # TODO

    #worker.fill_excel()  # TODO

    #worker.create_picture_folder()  # TODO


if __name__ == "__main__":
    create_folder_structure()
    # process_raw()
