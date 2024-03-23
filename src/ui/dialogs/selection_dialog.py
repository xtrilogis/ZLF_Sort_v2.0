from PyQt5 import QtCore
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLabel, QListView


class SelectionDialog(QDialog):
    """Dialog with a checkbox for every given item"""

    def __init__(self, title: str, message: str, items: list, parent=None):
        """parameter
        :arg title window title
        :arg message text displayed before the item list
        :arg items list of items"""
        super(SelectionDialog, self).__init__(parent=parent)
        self.setWindowTitle(title)
        form = QFormLayout(self)
        form.addRow(QLabel(message))
        self.listView = QListView(self)
        form.addRow(self.listView)
        model = QStandardItemModel(self.listView)
        for item in items:
            # create an item with a caption
            standardItem = QStandardItem(item)
            standardItem.setCheckable(True)
            model.appendRow(standardItem)
        self.listView.setModel(model)

        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self
        )
        form.addRow(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def itemsSelected(self):
        """gets all selected items
        :returns selected item list"""
        selected = []
        model = self.listView.model()
        i = 0
        while model.item(i):
            if model.item(i).checkState():
                selected.append(model.item(i).text())
            i += 1
        return selected
