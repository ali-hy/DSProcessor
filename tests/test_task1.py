import json
from typing import List
import unittest

from dsp.enums.graph_function import GRAPH_FUNCTION
from dsp.models import DigitalSignal, TimeSignal, FrequencySignal

class TestTask1(unittest.TestCase):
    src = "data/task1/"

    def compare_signals(self, signal: DigitalSignal, expected: DigitalSignal):
        for i in range(len(signal.signal_data)):
            for j in range(len(signal.signal_data[i])):
                self.assertAlmostEqual(signal.signal_data[i][j], expected.signal_data[i][j], places=6)

    def test_read_file_normal(self):
        src = f"{self.src}readfile/"

        # Read file
        signal = DigitalSignal.read(f"{src}input_normal.txt")
        self.assertIsInstance(signal, DigitalSignal)

        # Load expected result
        result = None
        with open(f"{src}result_normal.json") as file:
            result = json.load(file)

        for i in range(len(signal.signal_data)):
            self.assertListEqual(signal.signal_data[i], result[i])

    def test_generate_wave(self):
        src = f"{self.src}generate_wave/"

        params = [{
            "function": GRAPH_FUNCTION.SINE,
            "amplitude": 3,
            "analog_freq": 360,
            "sampling_freq": 720,
            "phase_shift": 1.96349540849362
        }, {
            "function": GRAPH_FUNCTION.COS,
            "amplitude": 3,
            "analog_freq": 200,
            "sampling_freq": 500,
            "phase_shift": 2.35619449019235
        }]

        signals: List[TimeSignal] = []

        for param in params:
            signals.append(TimeSignal.generate_wave(**param, save_to=f'{src}output_{param["function"].name.lower()}.txt'))

        expected_signals = [
            DigitalSignal.read(f'{src}result_sine.txt'),
            DigitalSignal.read(f'{src}result_cos.txt')
        ]

        for i, sig in enumerate(signals):
            self.compare_signals(sig, expected_signals[i])

        # for i in range(len(signals)):


        # # Generate wave
        # signal = TimeSignal.generate_wave(GRAPH_FUNCTION.SINE, 1, 200, 0, 500, f'{src}output_normal.txt')


if __name__ == "__main__":
    unittest.main()
