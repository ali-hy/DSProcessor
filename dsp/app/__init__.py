from typing import Any, Literal
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QToolBar,
    QMenu,
    QAction,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QErrorMessage
)
import sys
from dsp.app.components.number_dialog import NumberDialog
from dsp.enums.arithmetic_op import ARITHMETIC_OP
from dsp.enums.graph_type import GRAPH_TYPE
from dsp.models import DigitalSignal, TimeSignal
from dsp.app.components import MplCanvas
from dsp.models.FrequencySignal import FrequencySignal


class MainWindow(QMainWindow):
    __signal: DigitalSignal | None = None
    __graph_type_btns: QHBoxLayout | None = None

    @property
    def signal(self):
        return self.__signal

    @signal.setter
    def signal(self, signal: DigitalSignal):
        '''
        Function called when assigning a value to self.signal
        It will graph the signal after it is set

        Example:
        self.signal = DigitalSignal.read("path/to/file")
        '''

        self.__signal = signal
        self.graph_signal(self.signal)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DSProcessor")
        self.init_toolbar()

        self.__menuBar = self.menuBar()
        self.init_file_menu()
        self.init_arithmetic_operations_menu()
        self.init_quantize_menu()
        self.init_frequency_domain_menu()
        self.init_time_domain_menu()

        self.__layout = QVBoxLayout()
        self.__main_widget = QWidget()
        self.__main_widget.setLayout(self.__layout)
        self.setCentralWidget(self.__main_widget)

        self.__canvas = None

        self.setGeometry(100, 100, 800, 600)

        self.show()

    def init_toolbar(self):
        toolbar = QToolBar("DSP Toolbar")
        self.addToolBar(toolbar)

    def init_file_menu(self):
        """
        Add a "File" menu to the application.

        Actions:
        - Open: open a file and load it into the window
        - Save (Not implemented): save the currently open file
        - Generate wave (Not implemented): generate a new wave
        """
        menu = QMenu("File", self)

        # Open
        def show_open_file_dialog(slot: Any):
            self.open_single_file(self.get_file_input())

        open_action = QAction("Open", self)
        open_action.triggered.connect(show_open_file_dialog)
        menu.addAction(open_action)

        # Save
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_signal)
        menu.addAction(save_action)

        # Generate
        generate_action = QAction("Generate...")

        if self.__menuBar:
            self.__menuBar.addMenu(menu)

    def save_signal(self):
        assert self.__signal

        save_path = self.get_file_output()
        if not save_path:
            return

        self.__signal.save(save_path)

    def init_arithmetic_operations_menu(self):
        """
        Add a "Arithmetic Operations" menu to application

        Actions:
        - Add
        - Sub: subtract two signals
        - Multiply: multiply a signal by a scalar
        - Squuare: multiplies each position in the signal amplitude by itself (i.e. amp[i] * amp[i] for every i in sample_count)
        - Cumulative sum: calculates the cumalative sum of the signal
        """

        menu = QMenu("Arithmetic Operations", self)

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

        def handle_operation(operation: ARITHMETIC_OP):
            assert self.signal

            try:
                if operation == ARITHMETIC_OP.ADD:
                    op_result = self.signal + DigitalSignal.read(self.get_file_input())
                elif operation == ARITHMETIC_OP.SUB:
                    op_result = self.signal + DigitalSignal.read(self.get_file_input())
                elif operation == ARITHMETIC_OP.SQR:
                    op_result = self.signal.square()
                elif operation == ARITHMETIC_OP.ACC:
                    op_result = self.signal.cumulative_sum()
                elif operation == ARITHMETIC_OP.MUL:
                    op_result = self.signal * self.get_number_input_input("Scalar")
            except ValueError as e:
                self.show_error_message(e, "Invalid operation")
                return

            self.signal = op_result

        add_btn.triggered.connect(lambda: handle_operation(ARITHMETIC_OP.ADD))
        sub_btn.triggered.connect(lambda: handle_operation(ARITHMETIC_OP.SUB))
        square_btn.triggered.connect(lambda: handle_operation(ARITHMETIC_OP.SQR))
        csum_btn.triggered.connect(lambda: handle_operation(ARITHMETIC_OP.ACC))
        mul_btn.triggered.connect(lambda: handle_operation(ARITHMETIC_OP.MUL))

        menubar = self.menuBar()
        assert menubar
        menubar.addMenu(menu)

    def init_quantize_menu(self):
        """
        Add a "Quantize" menu to application

        Actions:
        - Bits: ask the user for the bit-depth available for quantization
        - Levels: ask the user for the number of levels to use for quantization
        """
        menu = QMenu("Quantize", self)

        # Actions
        bits_btn = menu.addAction("Bits")
        levels_btn = menu.addAction("Levels")

        assert levels_btn
        assert bits_btn

        def handle_quantize(quantize_type: Literal["Bits", "Levels"]):
            """
            Handle the flow of quantization, then quantize depending on <quantize-type>

            @param quantize_type: type of input for the quantization. Either "Bits" or "Levels" depending on the action used
            @type quantize_type: "Bits" | "Levels"

            Logic:
            1. Get input (file and number)
            2. Use signal quantization function depending on the input
            3. Create a new signal from the quantized data
            4. Graph that signal
            """
            signal = DigitalSignal.read(self.get_file_input())
            depth = self.get_number_input(quantize_type)

            assert isinstance(depth, int)

            quantized_data: list[list[str | float | int]] = []

            if quantize_type == "Levels":
                quantized_data = signal.quantize_w_levels(depth)
            elif quantize_type == "Bits":
                quantized_data = signal.quantize_w_bits(depth)

            quantized_signal = TimeSignal(
                signal.is_periodic,
                signal.sample_count,
                [
                    list(range(signal.sample_count)),
                    quantized_data[1] if quantize_type == "Bits" else quantized_data[2],  # type: ignore
                ],
            )

            self.signal = quantized_signal

        levels_btn.triggered.connect(lambda: handle_quantize("Levels"))
        bits_btn.triggered.connect(lambda: handle_quantize("Bits"))

        menubar = self.menuBar()
        assert menubar

        menubar.addMenu(menu)

    def init_frequency_domain_menu(self):
        '''
        Add a "Frequency Domain" menu to the application

        Actions:
        - DFT load a file in the time domain and switch it to the frequency domain DFT
        - IDFT load a file in the frequency domain and switch it to the time domain using IDFT
        '''
        menu = QMenu("Frequency Domain", self)

        # Actions
        dft_btn = menu.addAction("DFT")
        idft_btn = menu.addAction("IDFT")
        dct_btn = menu.addAction("DCT")

        assert dft_btn
        assert idft_btn
        assert dct_btn

        def handle_frequency_domain(operation: str):
            signal = DigitalSignal.read(self.get_file_input())

            if operation == "DFT":
                assert isinstance(signal, TimeSignal)
            elif operation == "IDFT":
                assert isinstance(signal, FrequencySignal)

            if operation == "DCT":
                assert isinstance(signal, TimeSignal)
                signal = signal.dct()
            else:
                signal = signal.switch_domain(self.get_number_input("Sampling freq"))

            self.signal = signal
            signal.save(f"data/task4/output_{operation}.txt")

        dft_btn.triggered.connect(lambda: handle_frequency_domain("DFT"))
        idft_btn.triggered.connect(lambda: handle_frequency_domain("IDFT"))
        dct_btn.triggered.connect(lambda: handle_frequency_domain("DCT"))

        menubar = self.menuBar()
        assert menubar

        menubar.addMenu(menu)

    def init_time_domain_menu(self):
        '''
        Add a "Time Domain" menu to application

        Actions:
        - Sharpening
            - First derivative
            - Second derivative
        - Fold
        - Shift
        '''

        menu = QMenu("Time Domain", self)

        # Actions
        sharpening_menu = menu.addMenu("Sharpening")
        fold_btn = menu.addAction("Fold")
        shift_btn = menu.addAction("Shift")
        smooth_btn = menu.addAction("Smooth")
        convolve_btn = menu.addAction("Convolve")

        assert sharpening_menu
        assert fold_btn
        assert shift_btn
        assert smooth_btn
        assert convolve_btn

        first_derivative_btn = sharpening_menu.addAction("First Derivative")
        second_derivative_btn = sharpening_menu.addAction("Second Derivative")

        assert first_derivative_btn
        assert second_derivative_btn

        def handle_time_domain(operation: str):
            assert isinstance(self.signal, TimeSignal)

            if operation == "Fold":
                self.signal = self.signal.folded()
            elif operation == "Shift":
                shift = self.get_number_input("Shift amount", "int")
                assert isinstance(shift, int)
                self.signal = self.signal.shifted(shift)
            elif operation == "First Derivative":
                self.signal = self.signal + self.signal.first_derivative()
            elif operation == "Second Derivative":
                self.signal = self.signal - self.signal.second_derivative()
            elif operation == "Advanced Fold":
                self.signal = self.signal.shifted(int(self.get_number_input("Shift by", "int"))).folded()
            elif operation == "Smooth":
                self.signal = self.signal.smoothed(int(self.get_number_input("Window size", "int")))
            elif operation == "Convolve":
                in_file = self.get_file_input()
                if not in_file:
                    return
                sig2 = DigitalSignal.read(in_file)
                assert isinstance(sig2, TimeSignal)
                self.signal = self.signal.convolved(sig2)

        fold_btn.triggered.connect(lambda: handle_time_domain("Fold"))
        shift_btn.triggered.connect(lambda: handle_time_domain("Shift"))
        first_derivative_btn.triggered.connect(lambda: handle_time_domain("First Derivative"))
        second_derivative_btn.triggered.connect(lambda: handle_time_domain("Second Derivative"))
        smooth_btn.triggered.connect(lambda: handle_time_domain("Smooth"))
        convolve_btn.triggered.connect(lambda: handle_time_domain("Convolve"))

        menubar = self.menuBar()
        assert menubar

        menubar.addMenu(menu)

    def open_single_file(self, file_path: str | None):
        if not file_path:
            return

        action_buttons = QHBoxLayout()
        self.signal = DigitalSignal.read(file_path)

        graph_button = QPushButton("Continious Graph")
        graph_button.clicked.connect(lambda: self.graph_signal(self.__signal, GRAPH_TYPE.CONTINUOUS))
        action_buttons.addWidget(graph_button)

        graph_button = QPushButton("Discrete Graph")
        graph_button.clicked.connect(
            lambda: self.graph_signal(self.__signal, GRAPH_TYPE.DISCRETE)
        )
        action_buttons.addWidget(graph_button)

        graph_button = QPushButton("Both Graph")
        graph_button.clicked.connect(
            lambda: self.graph_signal(self.__signal, GRAPH_TYPE.BOTH_ON_PALLETE)
        )
        action_buttons.addWidget(graph_button)

        graph_button = QPushButton("Separate Graph")
        graph_button.clicked.connect(
            lambda: self.graph_signal(self.__signal, GRAPH_TYPE.SEPARATE)
        )
        action_buttons.addWidget(graph_button)

        self.__layout.addLayout(action_buttons)

    def get_file_input(self):
        file_path = QFileDialog.getOpenFileName(self, "Open file", filter="*.txt")[0]
        return file_path if len(file_path) > 0 else None

    def get_file_output(self):
        file_path = QFileDialog.getSaveFileName(self, "Save File", filter="*.txt")[0]
        return file_path if len(file_path) > 0 else None

    def get_number_input(self, label: str, num_type: Literal["int", "float"] = "float"):
        dialog = NumberDialog(label, num_type)
        dialog.exec()
        return dialog.value

    def graph_signal(self, signal: DigitalSignal | None, type=GRAPH_TYPE.CONTINUOUS):
        if (signal is None):
            return

        if (isinstance(signal, FrequencySignal)):
            type = GRAPH_TYPE.DISCRETE

        if (self.__canvas):
            self.__layout.removeWidget(self.__canvas)
        self.__canvas = MplCanvas()
        self.__layout.addWidget(self.__canvas)

        signal.graph_wave(type, self.__canvas.fig)
        self.__layout.addWidget(self.__canvas)

    def show_error_message(self, error: Exception, note: str):
        error.add_note(note)
        QErrorMessage(self).showMessage(f"ERROR: {error}")

app = QApplication(sys.argv)
window = MainWindow()


def start_app():
    window.show()
    app.exec()
