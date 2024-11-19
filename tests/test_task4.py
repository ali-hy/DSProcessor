import unittest

from dsp.models import DigitalSignal, FrequencySignal, TimeSignal
from tests.funcs.compareFreqDom import SignalComapreAmplitude, SignalComaprePhaseShift


class TestTask4(unittest.TestCase):
    src = "data/task4/"

    def test_dft(self):
        signal = DigitalSignal.read(self.src + "input.txt")
        result = signal.switch_domain(4)
        assert isinstance(result, FrequencySignal)

        result.save(self.src + "output_dft_test.txt")
        expected = DigitalSignal.read(self.src + "result.txt")
        assert isinstance(expected, FrequencySignal)

        self.assertTrue(
            SignalComapreAmplitude(result["amp"], expected["amp"])
        )
        print("\nAmplitude Test Passed\n")

        self.assertTrue(
            SignalComaprePhaseShift(result["pshift"], expected["pshift"])
        )
        print("\nPhase Shift Test Passed\n")

    def test_idft(self):
        signal = DigitalSignal.read(self.src + "result.txt")
        result = signal.switch_domain(4)
        assert isinstance(result, TimeSignal)

        result.save(self.src + "output_idft_test.txt")
        expected = DigitalSignal.read(self.src + "input.txt")
        assert isinstance(expected, TimeSignal)

        self.assertTrue(
            SignalComapreAmplitude(result["amp"], expected["amp"])
        )
        print("\nAmplitude Test Passed\n")
