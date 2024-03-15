# ##### This file is only for building and testing new modules ##### #
# ##### Working Code needs to be included in the project-code  ##### #
import os
import shutil
import sys
from datetime import date

import pandas as pd
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

BASE = "D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/"
FILE_ROOT_LOCATION = BASE + "finale Tests Basics/Bilder_Videos/Rohmaterial/"
FILE_EXCEL = (
    BASE + "finale Tests Basics/Bilder_Videos/Rohmaterial\\Zeltlagerfilm 2022.xlsx"
)
FILE_DST = BASE + "finale Tests Basics/Bilder_Videos/Schnittmaterial/"
"""
Notes:
    Finale Material Ordner:
    - tag_Bilder_Videos tag_pic_vid
    - Rohmaterial
    - Bilder_Videos Pic_Vid
"""


class RawMaterialPreset:
    def __init__(self, filmordner):
        self.filmordner = filmordner

    def check_input(self):
        # Rohmaterilpfad richtig? Path exists
        # Excelpfad richtig Excel exists
        pass

    def problem_with_raw_material(self):
        """Checks if all video- and picture files are stored in 'Rohmaterial'
        :returns str if files found outside 'Rohmaterial', else nan"""
        extensions = [".JPG", "jpg", ".NEF", ".PNG", ".MOV", ".MTS", ".MP4"]
        for root, _, files in os.walk(self.filmordner):
            if "Rohmaterial" in root:
                continue
            for file in files:
                filename, file_ext = os.path.splitext(file)
                if file_ext in extensions:
                    return True
        return False

    def check_excel_exists(self):
        for root, _, files in os.walk(self.filmordner):
            for file in files:
                if ".xlsx" in file:
                    print("Excel gefunden.")
                    # ### prüfen, ob sich die Excel öffnen lässt und das Spalten minimum enthält
                    return os.path.join(root, file)
        return self.create_empty_excel()

    def create_empty_excel(self):
        excel_filename = "Zeltlagerfilm 2022.xlsx"
        path_excel = os.path.join(self.filmordner, excel_filename)
        df_videos = pd.DataFrame(
            columns=["Datei", "Tag", "Abschnitt", "Bewertung", "Bemerkung"]
        )
        df_pictures = pd.DataFrame(
            columns=["Datei", "Tag", "Abschnitt", "Bewertung", "Bemerkung"]
        )

        writer = pd.ExcelWriter(path_excel, engine="xlsxwriter")
        df_videos.to_excel(writer, index=False, sheet_name="Videos")
        df_pictures.to_excel(writer, index=False, sheet_name="Bilder")
        writer.save()
        print("New Excel created")

    def check_raw_preset(self):
        # Pfade validieren
        if self.problem_with_raw_material():
            print(
                "Please make sure all video and picture files are stored within '/Rohmaterial'"
            )
        self.check_excel_exists()
        # check_excel_content(excel_path= excel)


class ProcessExcelPreset:
    def __init__(self):
        pass

    def check_excel(self):
        # lässt sich öffnen
        # enthält mindestens
        # - sheet Video mit Spalten Datei, Abschnitt, Bewertung, Bemerkung
        # - sheet Bilder Datei, Abschnitt, Bewertung, Bemerkung
        pass

    def validate_paths(self):
        # Excel Pfad
        # Raw Material Pfad
        # Destination_root
        # check inputs
        pass

    def validate_inputs(self):
        # Marker - string
        # Divider - string
        # Spalten - sting contains Divider
        # Grenze - int
        pass


def gui_test():
    # https://build-system.fman.io/pyqt5-tutorial
    app = QApplication([])
    window = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(QPushButton("Top"))
    layout.addWidget(QPushButton("Bottom"))
    window.setLayout(layout)
    window.show()

    # run until user closes it
    app.exec()


class ScrollLabel(QScrollArea):
    # constructor
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        # making widget resizable
        self.setWidgetResizable(True)

        # making qwidget object
        content = QWidget(self)
        self.setWidget(content)

        # vertical box layout
        lay = QVBoxLayout(content)

        # creating label
        self.label = QLabel("test\n test", content)

        # setting alignment to the text
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # making label multi-line
        self.label.setWordWrap(True)

        # adding label to the layout
        lay.addWidget(self.label)

    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # informations
        info = "info"
        new_info = "new info "

        # set the title
        self.setWindowTitle("Label")

        # setting  the geometry of window
        self.setGeometry(0, 0, 400, 300)
        layout = QHBoxLayout(self)

        # creating a label widget
        self.label_1 = ScrollLabel(self)

        # moving position
        self.label_1.move(100, 100)

        self.pb = QToolButton(self)
        # folder icon
        self.pb.setIcon(
            QIcon(
                "D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/icon0-vector-351-01.jpg"
            )
        )
        layout.addWidget(self.label_1)
        layout.addWidget(self.pb)
        self.pb.move(150, 150)
        self.pb.clicked.connect(self.pushed)
        # show all the widgets
        self.show()

    def pushed(self):
        directory = QFileDialog.getExistingDirectory(
            parent=self, caption="Open dir", directory="C:\\"
        )
        # test = self.label_1.label.text()
        self.label_1.setText(directory)
        # add scrollbar for text field


# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
# window = Window()

# start the app
# sys.exit(App.exec())
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *


class combo(QComboBox):
    def __init__(self, title, parent):
        super(combo, self).__init__(parent)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        print
        e

        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        self.addItem(e.mimeData().text())


class Example(QWidget):
    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):
        lo = QFormLayout()
        lo.addRow(QLabel("Type some text in textbox and drag it into combo box"))

        edit = QLineEdit()
        edit.setDragEnabled(True)
        com = combo("Button", self)
        lo.addRow(edit, com)
        self.setLayout(lo)
        self.setWindowTitle("Simple drag & drop")


def main():
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    app.exec_()


import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *  # type: ignore
from PyQt5.QtWidgets import QApplication


class inputdialogdemo(QWidget):
    def __init__(self, parent=None):
        super(inputdialogdemo, self).__init__(parent)
        self.test = ""

        layout = QFormLayout()
        self.le0 = QLabel()
        self.le0.setText("Format: 25.07.2019 14:33:20")
        self.btn1 = QPushButton("OK")
        self.btn1.clicked.connect(self.gettext)

        self.le1 = QLineEdit()
        layout.addRow(self.le0)
        layout.addRow(self.le1, self.btn1)

        self.setLayout(layout)
        self.setWindowTitle("Datum")

    def gettext(self):
        print(self.le1.text())
        self.test = self.le1.text()
        self.close()


def main2():
    app = QApplication(sys.argv)
    ex = inputdialogdemo()
    ex.show()
    print(ex.test)
    app.exec_()
