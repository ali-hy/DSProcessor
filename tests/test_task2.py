import json
from typing import List
import unittest

from dsp.enums.graph_function import GRAPH_FUNCTION
from dsp.models import DigitalSignal, TimeSignal, FrequencySignal


class TestTask2(unittest.TestCase):
    src = "data/task2/input/"
    dest = "data/task2/"

    signal1 = DigitalSignal.read(f"{src}sig1.txt")
    signal2 = DigitalSignal.read(f"{src}sig2.txt")
    signal3 = DigitalSignal.read(f"{src}sig3.txt")

    def test_add(self):
        dest = f"{self.dest}add/"

        # Read result files
        expected_signal1p2 = DigitalSignal.read(f"{dest}result_sig1+sig2.txt")
        expected_signal1p3 = DigitalSignal.read(f"{dest}result_sig1+sig3.txt")

        # Add signals
        result_signal1p2 = self.signal1 + self.signal2
        result_signal1p3 = self.signal1 + self.signal3

        result_signal1p2.save(f"{dest}output_sig1+sig2.txt")
        result_signal1p3.save(f"{dest}output_sig1+sig3.txt")

        self.assertTrue(expected_signal1p2.compare(result_signal1p2))
        self.assertTrue(result_signal1p3.compare(expected_signal1p3))

    def test_sub(self):
        dest = f"{self.dest}sub/"

        # Read result files
        expected_signal1m2 = DigitalSignal.read(f"{dest}result_sig1-sig2.txt")
        expected_signal1m3 = DigitalSignal.read(f"{dest}result_sig1-sig3.txt")

        # Subtract signals
        result_signal1m2 = self.signal1 - self.signal2
        result_signal1m3 = self.signal1 - self.signal3

        result_signal1m2.save(f"{dest}output_sig1-sig2.txt")
        result_signal1m3.save(f"{dest}output_sig1-sig3.txt")

        self.assertTrue(expected_signal1m2.compare(result_signal1m2))
        self.assertTrue(result_signal1m3.compare(expected_signal1m3))

    def test_mul(self):
        dest = f"{self.dest}mul/"

        # Read result files
        expected_signal1x2 = DigitalSignal.read(f"{dest}result_sig1x5.txt")
        expected_signal1x3 = DigitalSignal.read(f"{dest}result_sig2x10.txt")

        # Multiply signals
        result_signal1x5 = self.signal1 * 5
        result_signal2x10 = self.signal2 * 10

        result_signal1x5.save(f"{dest}output_sig1x5.txt")
        result_signal2x10.save(f"{dest}output_sig2x10.txt")

        self.assertTrue(expected_signal1x2.compare(result_signal1x5))
        self.assertTrue(result_signal2x10.compare(expected_signal1x3))

    def test_square(self):
        dest = f"{self.dest}sqr/"

        # Read result files
        expected_signal1sqr = DigitalSignal.read(f"{dest}result_sig1sqr.txt")

        # Square signals
        result_signal1sqr = self.signal1.square()

        result_signal1sqr.save(f"{dest}output_sig1sqr.txt")

        self.assertTrue(expected_signal1sqr.compare(result_signal1sqr))

    def test_cumulative_sum(self):
        dest = f"{self.dest}csum/"

        # Read result files
        expected_signal1cumsum = DigitalSignal.read(f"{dest}result_sig1csum.txt")

        # Cumulative sum
        result_signal1cumsum = self.signal1.cumulative_sum()

        result_signal1cumsum.save(f"{dest}output_sig1csum.txt")

        self.assertTrue(expected_signal1cumsum.compare(result_signal1cumsum))

if __name__ == "__main__":
    unittest.main()
