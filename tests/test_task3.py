import unittest

from dsp.models import DigitalSignal, TimeSignal
from tests.funcs.QuanTest1 import QuantizationTest1
from tests.funcs.QuanTest2 import QuantizationTest2


class TestTask3(unittest.TestCase):
    src = "data/task3/"

    def test_quantization_with_bits(self):
        signal_in = DigitalSignal.read(self.src + "Quan1_input.txt")
        quantized_signal = signal_in.quantize_w_bits(
            3, save_path=self.src + "output_Quan1.txt"
        )

        self.assertTrue(
            QuantizationTest1(
                self.src + "Quan1_output.txt",
                quantized_signal[0],
                quantized_signal[1],
            )
        )

    def test_quantization_with_levels(self):
        signal_in = TimeSignal.read(self.src + "Quan2_input.txt")
        quantized_signal = signal_in.quantize_w_levels(4, save_path=self.src + "output_Quan2.txt")

        self.assertTrue(
            QuantizationTest2(
                self.src + "Quan2_output.txt",
                quantized_signal[0],
                quantized_signal[1],
                quantized_signal[2],
                quantized_signal[3],
            )
        )


if __name__ == "__main__":
    unittest.main()
