import unittest

from dsp.enums.filter_type import FILTER_TYPE
from dsp.models import DigitalSignal, FrequencySignal, TimeSignal
from dsp.models.Filter import FirFilter
from tests.funcs.compareSignals import Compare_Signals


class TestFirFilters(unittest.TestCase):
    src = "data/task7/Sampling test cases/"

    def test_downsampling(self):
        fil = FirFilter(
            filter_type=FILTER_TYPE.LOW_PASS,
            cutoff=1500,
            sampling_frequency=8000,
            stopband_attenuation=50,
            transition_band=500
        )

        signal = DigitalSignal.read("data/task7/Sampling test cases/Testcase 1/ecg400.txt")
        assert isinstance(signal, TimeSignal)

        res = signal.downsample(2, fil)
        res.save(f"{self.src}Testcase 1/output.txt")

        self.assertTrue(
            Compare_Signals(f"{self.src}Testcase 1/Sampling_Down.txt", res["time"], res["amp"])
        )

    def test_upsampling(self):
        fil = FirFilter(
            filter_type=FILTER_TYPE.LOW_PASS,
            cutoff=1500,
            sampling_frequency=8000,
            stopband_attenuation=50,
            transition_band=500
        )

        signal = DigitalSignal.read("data/task7/Sampling test cases/Testcase 2/ecg400.txt")
        assert isinstance(signal, TimeSignal)

        res = signal.upsample(3, fil)
        res.save(f"{self.src}Testcase 2/output.txt")

        self.assertTrue(
            Compare_Signals(f"{self.src}Testcase 2/Sampling_Up.txt", res["time"], res["amp"])
        )

    def test_resampling(self):
        fil = FirFilter(
            filter_type=FILTER_TYPE.LOW_PASS,
            cutoff=1500,
            sampling_frequency=8000,
            stopband_attenuation=50,
            transition_band=500
        )

        signal = DigitalSignal.read("data/task7/Sampling test cases/Testcase 3/ecg400.txt")
        assert isinstance(signal, TimeSignal)

        res = signal.resample(2, 3, fil)
        res.save(f"{self.src}Testcase 3/output.txt")

        self.assertTrue(
            Compare_Signals(f"{self.src}Testcase 3/Sampling_Up_Down.txt", res["time"], res["amp"])
        )
