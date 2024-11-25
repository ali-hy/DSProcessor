from typing import Any, Dict, List, Literal, Callable
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QDialogButtonBox,
)
from PyQt5.QtGui import QDoubleValidator, QIntValidator


class NumberDialog(QDialog):
    def __init__(self, name: str, type: Literal["int", "float"] = "float"):
        super().__init__()
        self.value: int | float = 0
        self.num_type = type
        self.setWindowTitle(f"{name} Dialog")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        self.setLayout(layout)

        label, text_input = self.create_number_input(name)

        layout.addWidget(label)
        layout.addWidget(text_input)

        layout.addWidget(self.buttonBox)
        self.show()

    def create_number_input(self, name: str):
        label = QLabel(name)

        text_input = QLineEdit()

        validator = QDoubleValidator() if self.num_type == "float" else QIntValidator()

        text_input.setValidator(validator)

        def on_text_changed():
            try:
                self.value = (
                    float(text_input.text() or 0)
                    if self.num_type == "float"
                    else int(text_input.text() or 0)
                )
            except:
                self.value = 0

        text_input.textChanged.connect(on_text_changed)

        return label, text_input


class InputField:
    validators = {"float": QDoubleValidator, "int": QIntValidator}

    def __init__(self, name, type: Literal["int", "float", "str"], default: Any = None):
        self.name = name
        self.type = type
        self.default = default

    def create_ui(
        self, parent: QWidget | None = None, on_change: Callable | None = None
    ):
        label = QLabel(self.name)
        text_input = QLineEdit()

        if self.type in self.validators:
            text_input.setValidator(
                getattr(self.validators, self.type)
            )

        if on_change:
            text_input.textChanged.connect(on_change)


        if parent:
            layout = parent.layout()
            assert layout

            layout.addChildWidget(label)
            layout.addChildWidget(text_input)

        return label, text_input


class InputDialog(QDialog):
    def __init__(self, fields: List[InputField], name = "Required data"):
        super().__init__()
        self.value: int | float = 0
        self.num_type = type
        self.setWindowTitle(f"{name}")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        self.setLayout(layout)

        label, text_input = self.create_number_input(name)

        layout.addWidget(label)
        layout.addWidget(text_input)

        layout.addWidget(self.buttonBox)
        self.show()
