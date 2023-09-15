from os import path
from PyQt5 import QtWidgets


class DropLineEditExcel(QtWidgets.QLineEdit):
    """Allows to drag and drop a .xlsx-file, QLineEdit is set to Excel url"""

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        md = event.mimeData()

        if md.hasUrls():
            files = []
            for url in md.urls():
                if ".xlsx" in url.toLocalFile():
                    files.append(url.toLocalFile())

            self.setText(" ".join(files))
            event.acceptProposedAction()


class DropLineEditFolder(QtWidgets.QLineEdit):
    """Allows to drag and drop a folder, QLineEdit is set to folder url"""
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        md = event.mimeData()

        if md.hasUrls():
            files = []
            for url in md.urls():
                if path.isdir(url.toLocalFile()):
                    files.append(url.toLocalFile())

            self.setText(" ".join(files))
            event.acceptProposedAction()
