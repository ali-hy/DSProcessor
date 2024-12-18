import unittest

from dsp.models import DigitalSignal, FrequencySignal, TimeSignal
from tests.funcs.ConvTest import ConvTest
from tests.funcs.compareSignals import SignalSamplesAreEqual

class TestTask5(unittest.TestCase):
    src = "data/task6/"

    def test_moving_avg(self):
        src = "data/task2/input/"
        dest = f"{self.src}moving-avg/"

        signal = DigitalSignal.read(f"{src}sig1.txt")
        assert isinstance(signal, TimeSignal)

        output1 = signal.smooth(3)
        output1.save(f"{dest}output-sig1-3.txt")
        assert isinstance(output1, TimeSignal)

        signal = DigitalSignal.read(f"{src}sig2.txt")
        assert isinstance(signal, TimeSignal)

        output2 = signal.smooth(5)
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

        output = signal1.convolve(signal2)
        assert isinstance(output, TimeSignal)

        output.save(f"{src}output-conv.txt")

        self.assertTrue(
            ConvTest(output["time"], output["amp"])
        )

    def test_remove_dc_time(self):
        src = f"{self.src}dc-component/"

        signal = DigitalSignal.read(f"{src}input-DC_component.txt")
        assert isinstance(signal, TimeSignal)

        output = signal.remove_dc()
        assert isinstance(output, TimeSignal)
        output.save(f"{src}output-DC_component.txt")

        self.assertTrue(
            SignalSamplesAreEqual(f"{src}result-DC_component.txt", output["time"], output["amp"])
        )

    def test_remove_dc_freq(self):
        src = f"{self.src}dc-component/"

        signal = DigitalSignal.read(f"{src}input-DC_component.txt").switch_domain()
        assert isinstance(signal, FrequencySignal)

        output = signal.remove_dc()
        output = output.switch_domain()
        assert isinstance(output, TimeSignal)

        output.save(f"{src}output-DC_component.txt")

        self.assertTrue(
            SignalSamplesAreEqual(f"{src}result-DC_component.txt", output["time"], output["amp"])
        )

    def test_correlation(self):
        src = f"{self.src}correlation/"

        signal1 = DigitalSignal.read(f"{src}input-signal1.txt")
        signal2 = DigitalSignal.read(f"{src}input-signal2.txt")
        assert isinstance(signal1, TimeSignal)
        assert isinstance(signal2, TimeSignal)

        output = signal1.correlate(signal2)
        assert isinstance(output, TimeSignal)

        output.save(f"{src}output.txt")

        print("Correlation: ", output["amp"])

        self.assertTrue(
            SignalSamplesAreEqual(f"{src}result.txt", output["time"], output["amp"])
        )
