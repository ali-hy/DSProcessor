from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QApplication
import sys
from collections import namedtuple

Option = namedtuple('Option', ['label', 'value'])

class RadioDialog(QDialog):
    def __init__(self, options: list[Option], title: str = "Select an option", message: str = "Please select an option:", parent: QDialog | None = None) -> None:
        super(RadioDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self._layout = QVBoxLayout(self)

        self.label = QLabel(message, self)
        self._layout.addWidget(self.label)

        self.comboBox = QComboBox(self)
        for option in options:
            self.comboBox.addItem(option.label, option.value)
        self._layout.addWidget(self.comboBox)

        self.okButton = QPushButton("OK", self)
        self.okButton.clicked.connect(self.accept)
        self._layout.addWidget(self.okButton)

        self.setLayout(self._layout)

    def get_selected_value(self) -> int:
        return self.comboBox.currentData()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    options = [Option("Option 1", 1), Option("Option 2", 2), Option("Option 3", 3)]
    dialog = RadioDialog(options)
    if dialog.exec_() == QDialog.Accepted:
        print("Selected value:", dialog.get_selected_value())
    sys.exit(app.exec_())
