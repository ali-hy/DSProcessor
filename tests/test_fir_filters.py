import unittest

from dsp.enums.filter_type import FILTER_TYPE
from dsp.models import DigitalSignal, FrequencySignal, TimeSignal
from dsp.models.Filter import FirFilter
from tests.funcs.compareSignals import Compare_Signals

class TestFirFilters(unittest.TestCase):
    src = "data/task7/FIR test cases/"

    def test_lowpass(self):
        # Filter coefficients
        fil = FirFilter(
            filter_type=FILTER_TYPE.LOW_PASS,
            cutoff=1500,
            sampling_frequency=8000,
            stopband_attenuation=50,
            transition_band=500
        ).to_signal()

        fil.save(f"{self.src}Testcase 1/output.txt")

        self.assertTrue(
            Compare_Signals(f"{self.src}Testcase 1/LPFCoefficients.txt", fil["time"], fil["amp"])
        )

        # Filtered signal
        signal = DigitalSignal.read(f"{self.src}Testcase 2/ecg400.txt")
        assert isinstance(signal, TimeSignal)

        res = signal.convolve(fil)
        self.assertTrue(
            Compare_Signals(f"{self.src}Testcase 2/ecg_low_pass_filtered.txt", res["time"], res["amp"])
        )

    def test_hightpass(self):
        # Filter coefficients
        fil = FirFilter(
            filter_type=FILTER_TYPE.HIGH_PASS,
            sampling_frequency=8000,
            stopband_attenuation=70,
            cutoff=1500,
            transition_band=500
        ).to_signal()

        fil.save(f"{self.src}Testcase 3/output.txt")

        self.assertTrue(
            Compare_Signals(f"{self.src}Testcase 3/HPFCoefficients.txt", fil["time"], fil["amp"])
        )

        # Filtered signal
        signal = DigitalSignal.read(f"{self.src}Testcase 4/ecg400.txt")
        assert isinstance(signal, TimeSignal)

        res = signal.convolve(fil)
        self.assertTrue(
            Compare_Signals(f"{self.src}Testcase 4/ecg_high_pass_filtered.txt", res["time"], res["amp"])
        )

    def test_bandpass(self):
        # Filter coefficients
        fil = FirFilter(
            filter_type=FILTER_TYPE.BAND_PASS,
            lowcutoff=150,
            highcutoff=250,
            sampling_frequency=1000,
            stopband_attenuation=60,
            transition_band=50
        ).to_signal()

        fil.save(f"{self.src}Testcase 5/output.txt")

        self.assertTrue(
            Compare_Signals(f"{self.src}Testcase 5/BPFCoefficients.txt", fil["time"], fil["amp"])
        )

        # Filtered signal
        signal = DigitalSignal.read(f"{self.src}Testcase 6/ecg400.txt")
        assert isinstance(signal, TimeSignal)

        res = signal.convolve(fil)
        self.assertTrue(
            Compare_Signals(f"{self.src}Testcase 6/ecg_band_pass_filtered.txt", res["time"], res["amp"])
        )

    def test_bandstop(self):
        # Filter coefficients
        fil = FirFilter(
            filter_type=FILTER_TYPE.BAND_STOP,
            sampling_frequency=1000,
            stopband_attenuation=60,
            lowcutoff=150,
            highcutoff=250,
            transition_band=50
        ).to_signal()

        fil.save(f"{self.src}Testcase 7/output.txt")

        self.assertTrue(
            Compare_Signals(f"{self.src}Testcase 7/BSFCoefficients.txt", fil["time"], fil["amp"])
        )

        # Filtered signal
        signal = DigitalSignal.read(f"{self.src}Testcase 8/ecg400.txt")
        assert isinstance(signal, TimeSignal)

        res = signal.convolve(fil)
        self.assertTrue(
            Compare_Signals(f"{self.src}Testcase 8/ecg_band_stop_filtered.txt", res["time"], res["amp"])
        )
