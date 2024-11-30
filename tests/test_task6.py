import unittest

from dsp.models import DigitalSignal, TimeSignal
from tests.funcs.ConvTest import ConvTest
from tests.funcs.compareSignals import SignalSamplesAreEqual

class TestTask5(unittest.TestCase):
    src = "data/task6/"

    def test_moving_avg(self):
        src = "data/task2/input/"
        dest = f"{self.src}moving-avg/"

        signal = DigitalSignal.read(f"{src}sig1.txt")
        assert isinstance(signal, TimeSignal)

        output1 = signal.smoothed(3)
        output1.save(f"{dest}output-sig1-3.txt")
        assert isinstance(output1, TimeSignal)

        signal = DigitalSignal.read(f"{src}sig2.txt")
        assert isinstance(signal, TimeSignal)

        output2 = signal.smoothed(5)
        output2.save(f"{dest}output-sig2-5.txt")
        assert isinstance(output2, TimeSignal)

        self.assertTrue(
            SignalSamplesAreEqual(f"{dest}result-MovAvgTest1.txt", output1["time"], output1["amp"])
        )

        self.assertTrue(
            SignalSamplesAreEqual(f"{dest}result-MovAvgTest2.txt", output2["time"], output2["amp"])
        )

    def test_convolution(self):
        src = f"{self.src}convolution/"

        signal1 = DigitalSignal.read(f"{src}input-conv_Sig1.txt")
        signal2 = DigitalSignal.read(f"{src}input-conv_Sig2.txt")
        assert isinstance(signal1, TimeSignal)
        assert isinstance(signal2, TimeSignal)

        output = signal1.convolved(signal2)
        assert isinstance(output, TimeSignal)

        output.save(f"{src}output-conv.txt")

        self.assertTrue(
            ConvTest(output["time"], output["amp"])
        )
