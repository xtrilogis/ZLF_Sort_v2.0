from PyQt5.QtCore import QDate

from ui import thread_worker as tw

ROOT = "../TestDateien"


def create_folder_structure():
    worker = tw.Worker()
    worker.setup_folder_structure(parent=ROOT, date=QDate(2023, 1, 1))


def process_raw():
    worker = tw.Worker()


if __name__ == "__main__":
    create_folder_structure()
