from typing import Any
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QToolBar, QMenu, QAction, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget
import sys
from dsp.app.components.number_dialog import NumberDialog
from dsp.enums.arithmetic_op import ARITHMETIC_OP
from dsp.enums.graph_type import GRAPH_TYPE
from dsp.models import DigitalSignal, TimeSignal
from dsp.app.components import MplCanvas


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DSProcessor")
        self.init_toolbar()

        self.__menuBar = self.menuBar()
        self.init_file_menu()
        self.init_arithmetic_operations_menu()
        self.init_quantize_menu()

        self.__layout = QVBoxLayout()
        self.__main_widget = QWidget()
        self.__main_widget.setLayout(self.__layout)
        self.setCentralWidget(self.__main_widget)

        self.setGeometry(100, 100, 800, 600)

        self.show()

    def init_toolbar(self):
        toolbar = QToolBar("DSP Toolbar")
        self.addToolBar(toolbar)

    def init_file_menu(self):
        menu = QMenu("File", self)

        # Open
        open_file_dialog = QFileDialog()
        open_file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        def show_open_file_dialog(slot: Any):
            open_file_dialog.exec()
            self.open_single_file(open_file_dialog.selectedFiles()[0])

        open_action = QAction("Open", self)
        open_action.triggered.connect(show_open_file_dialog)

        menu.addAction(open_action)

        # Save
        save_action = QAction("Save", self)

        generate_action = QAction("Generate...")


        if (self.__menuBar):
            self.__menuBar.addMenu(menu)

    def init_arithmetic_operations_menu(self):
        menu = QMenu("Arithmetic Operations", self)
        op_result: DigitalSignal | None = None

        # Actions
        add_btn = menu.addAction("Add")
        sub_btn = menu.addAction("Sub")
        mul_btn = menu.addAction("Multiply")
        square_btn = menu.addAction("Square")
        csum_btn = menu.addAction("Cumulative sum")

        assert add_btn
        assert sub_btn
        assert mul_btn
        assert square_btn
        assert csum_btn

        # Get file input
        open_file_dialog = QFileDialog()
        open_file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        def get_file():
            open_file_dialog.exec()
            return open_file_dialog.selectedFiles()[0]

        def get_number(label: str):
            dialog = NumberDialog(label, "int")
            dialog.exec()
            return dialog.value

        def handle_operation(operation: ARITHMETIC_OP):
            if operation == ARITHMETIC_OP.ADD:
                op_result = DigitalSignal.read(get_file()) + DigitalSignal.read(get_file())
            elif operation == ARITHMETIC_OP.SUB:
                op_result = DigitalSignal.read(get_file()) + DigitalSignal.read(get_file())
            elif operation == ARITHMETIC_OP.SQR:
                op_result = DigitalSignal.read(get_file()).square()
            elif operation == ARITHMETIC_OP.ACC:
                op_result = DigitalSignal.read(get_file()).cumulative_sum()
            elif operation == ARITHMETIC_OP.MUL:
                op_result = DigitalSignal.read(get_file()) * get_number("Scalar")

            self.graph_signal(op_result)

        add_btn.triggered.connect(lambda: handle_operation(ARITHMETIC_OP.ADD))
        sub_btn.triggered.connect(lambda: handle_operation(ARITHMETIC_OP.SUB))
        square_btn.triggered.connect(lambda: handle_operation(ARITHMETIC_OP.SQR))
        csum_btn.triggered.connect(lambda: handle_operation(ARITHMETIC_OP.ACC))
        mul_btn.triggered.connect(lambda: handle_operation(ARITHMETIC_OP.MUL))

        menubar = self.menuBar()
        assert menubar
        menubar.addMenu(menu)

    def init_quantize_menu(self):
        menu = QMenu("Quantize", self)

        # Actions
        bits_btn = menu.addAction("Bits")
        levels_btn = menu.addAction("Levels")

        assert levels_btn
        assert bits_btn

        # Get file input
        open_file_dialog = QFileDialog()
        open_file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        def get_file():
            open_file_dialog.exec()
            return open_file_dialog.selectedFiles()[0]

        def get_number(label: str):
            dialog = NumberDialog(label, "int")
            dialog.exec()
            return dialog.value

        def handle_quantize(quantize_type: str):
            signal = DigitalSignal.read(get_file())
            depth = get_number(quantize_type)

            assert isinstance(depth, int)

            quantized_data: list[list[str | float | int]] = []

            if quantize_type == "Levels":
                quantized_data = signal.quantize_w_levels(depth, save_path="data/task3/output_levels.txt")
            elif quantize_type == "Bits":
                quantized_data = signal.quantize_w_bits(depth, save_path="data/task3/output_bits.txt")

            quantized_signal = TimeSignal(signal.isPeriodic, signal.sample_count, [
                list(range(signal.sample_count)),
                quantized_data[1] if quantize_type == "Bits" else quantized_data[2] # type: ignore
            ])

            self.graph_signal(quantized_signal)

        levels_btn.triggered.connect(lambda: handle_quantize("Levels"))
        bits_btn.triggered.connect(lambda: handle_quantize("Bits"))

        menubar = self.menuBar()
        assert menubar

        menubar.addMenu(menu)

    def open_single_file(self, file_path: str):
        action_buttons = QHBoxLayout()
        signal = DigitalSignal.read(file_path)

        graph_button = QPushButton("Continious Graph")
        graph_button.clicked.connect(lambda: self.graph_signal(signal))
        action_buttons.addWidget(graph_button)

        graph_button = QPushButton("Discrete Graph")
        graph_button.clicked.connect(lambda: self.graph_signal(signal, GRAPH_TYPE.DISCRETE))
        action_buttons.addWidget(graph_button)

        graph_button = QPushButton("Both Graph")
        graph_button.clicked.connect(lambda: self.graph_signal(signal, GRAPH_TYPE.BOTH_ON_PALLETE))
        action_buttons.addWidget(graph_button)

        graph_button = QPushButton("Separate Graph")
        graph_button.clicked.connect(lambda: self.graph_signal(signal, GRAPH_TYPE.SEPARATE))
        action_buttons.addWidget(graph_button)

        self.__layout.addLayout(action_buttons)

    def graph_signal(self, signal: DigitalSignal, type=GRAPH_TYPE.CONTINUOUS):
        canvas = MplCanvas(self)
        signal.graph_wave(type, canvas.fig)
        print("Graphing signal")
        self.__layout.addWidget(canvas)



app = QApplication(sys.argv)
window = MainWindow()

def start_app():
    window.show()
    app.exec()
