
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QDialogButtonBox, QLabel
from qgis.PyQt.QtCore import Qt

class MultiSelectDialog(QDialog):
    def __init__(self,title, options, selected_option, parent=None):
        super(MultiSelectDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self.resize(300, 400)

        layout = QVBoxLayout(self)

        self.list_widget = QListWidget(self)

        for option in options:
            item = QListWidgetItem(option)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)

            if option in selected_option:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

            self.list_widget.addItem(item)

        layout.addWidget(self.list_widget)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_selected_options(self):
        selected_options = []
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if item.checkState() == Qt.Checked:
                selected_options.append(item.text())
        return selected_options