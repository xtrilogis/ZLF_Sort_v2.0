from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from assethandling.asset_manager import window_icon
from ui.stylesheets import msg_box_style



def basic_messagebox(title, message):
    """Creates a basic Messagebox with Information Icon and one "ok" button
    :arg title is set as the window title
    :arg message is set as the main text"""
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(QMessageBox.Information)
    msg.setWindowIcon(QtGui.QIcon(str(window_icon)))
    msg.setStyleSheet(msg_box_style)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.setDefaultButton(QMessageBox.Ok)
    return msg

# todo clean unnecessary code
def help_folder_creation():
    """Messagebox with ok Button and explanatory text"""
    message = (
        "Dieser Abschnitt erstellt alle nötigen Dateien\n"
        "und Ordner für den Zeltlagerfilm:\n"
        "- Zeltlagerfilm Excel\n"
        "- Ordner für Rohmaterial (Bilder und Videos pro Tag)\n"
        "- Ordner für alles weitere (Zusatzmaterial, ...)"
    )
    return basic_messagebox(title="Hilfe", message=message)


def help_raw_material():
    """Messagebox with ok Button and explanatory text"""
    message = (
        "Dieser Abschnitt erleichtert die Arbeit mit dem Rohmaterial.\n"
        "- Dateien werden automatisch nach ihrem Datum sortiert\n"
        "  benannt\n"
        "  Schema: Monat-Tag-Wochentag-Nr. innerhalb des Tages\n"
        "- Die Dateinamen werden in die Excel-Liste eingetragen, \n"
        "  für jeden neuen Ordner wird das jeweilige Datum eingetragen.\n"
        "- Alle Bilder werden in einen Bilderordner für die Diashow\n"
        "  kopiert."
    )
    return basic_messagebox(title="Hilfe", message=message)


def help_excel():
    """Messagebox with ok Button and explanatory text"""
    message = (
        "Dieser Abschnitt erleichtert das auswerten der Excel\n"
        "Alle Ergebnisse werden in den Ordner 'Schnittmaterial'\n"
        "- 'Abschnitte' wertet die Spalte 'Abschnitt' aus\n"
        "  > alle Dateien, die eine Bewertung >= der Angegebenen\n"
        "    haben, werden in /'Tag'/'Dateityp'/'Abschnitt' gespeichert.\n"
        "  > Bilder mit passender Bewertung erstellt einen Ordner \n"
        "    mit allen Bildern die eine Bewertung >= der \n"
        "    Angegebenen haben.\n"
        "- 'Selektionen' wertet die Angegebenen Spalten aus\n"
        "  > die Spalten werden nach dem 'Marker' durchsucht und\n"
        "    alle markierten werden unter /'Selektionen'/'Spalte'\n"
        "  > Wenn keine Spalte durchsucht werden soll, leer \n"
        "  > Wenn nur eine Spalte durchsucht werden soll,\n"
        "    Trennzeichen hinten anhängen\n"
        "  > Trennzeichen zwischen den einzelnen Spalten verwenden"
    )
    return basic_messagebox(title="Hilfe", message=message)


def problem_with_input(error: str):
    """Messagebox with ok Button, displaying the given error"""
    return basic_messagebox(title="Fehler", message=error)


def handle_problem_mc():
    """Messagebox explaining the problem with media creation date"""
    msg = QMessageBox()
    msg.setWindowTitle("Fehler")
    msg.setText(
        "Beim Einlesen der Videos Aufnahmezeiten ist ein Fehler aufgetreten."
        "\nEs kann nicht garantiert werden, dass die Dateien zeitlich richtig "
        "\nsortiert benannt werden."
        "\nEs gibt 4 Möglichkeiten:"
        "\n1. Die Dateien von Hand umbenennen."
        "\n2. Datum ändern, wenn möglich."
        "\n3. Datum eingeben, für die Videos, wo es nicht automatisch geht."
        "\n4. Das Problem ignorieren und Dateien ggf. nach teils falschem Datum "
        "sortiert benennen."
    )
    msg.setIcon(QMessageBox.Warning)
    msg.setStyleSheet(msg_box_style)
    msg.addButton(QtWidgets.QPushButton("Von Hand"), QMessageBox.AcceptRole)
    msg.addButton(QtWidgets.QPushButton("Wo möglich"), QMessageBox.RejectRole)
    msg.addButton(QtWidgets.QPushButton("Eingeben"), QMessageBox.ActionRole)
    msg.addButton(QtWidgets.QPushButton("Ignorieren"), QMessageBox.RejectRole)
    msg.setDefaultButton(QMessageBox.No)
    return msg


def excel_exists(message):
    """Creates a basic Messagebox with Information Icon and one "ok" button
    :arg message is set as the main text"""
    msg = QMessageBox()
    msg.setWindowTitle("Datei existiert")
    msg.setText(message)
    msg.setIcon(QMessageBox.Information)
    msg.setWindowIcon(QtGui.QIcon(str(window_icon)))
    msg.setStyleSheet(msg_box_style)
    msg.addButton(QtWidgets.QPushButton("Überschreiben"), QMessageBox.RejectRole)
    msg.setStandardButtons(QMessageBox.Abort)
    msg.setDefaultButton(QMessageBox.Abort)
    return msg
