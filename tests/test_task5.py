import unittest

from data.task5.DerivativeSignal import DerivativeSignal
from tests.funcs.Shift_Fold_Signal import Shift_Fold_Signal
from dsp.models import DigitalSignal, FrequencySignal, TimeSignal
from tests.funcs.compareSignals import SignalSamplesAreEqual

class TestTask5(unittest.TestCase):
    src = "data/task5/"

    def test_dct(self):
        src = f"{self.src}dct/"

        signal = DigitalSignal.read(f"{src}input.txt")
        assert isinstance(signal, TimeSignal)

        output = signal.dct()
        output.save(f"{src}output.txt")
        assert isinstance(output, FrequencySignal)

        expected = DigitalSignal.read(f"{src}result.txt")
        assert isinstance(expected, FrequencySignal)

        print(output["amp"])
        print(expected["pshift"])

        self.assertTrue(
            SignalSamplesAreEqual(f"{src}result.txt", output["freq"], output["amp"])
        )

    def test_fold(self):
        src = f"{self.src}folding/"

        signal = DigitalSignal.read(f"{src}input.txt")
        assert isinstance(signal, TimeSignal)

        output = signal.folded()
        self.assertTrue(
            Shift_Fold_Signal(f"{src}result-fold.txt", output["time"], output["amp"])
        )

        output = signal.shifted(500).folded()
        output.save(f"{src}output-shift_folded_by_500.txt")
        self.assertTrue(
            Shift_Fold_Signal(f"{src}result-shift_folded_by_500.txt", output["time"], output["amp"])
        )

        output = signal.shifted(-500).folded()
        output.save(f"{src}output-shift_folded_by_n500.txt")
        self.assertTrue(
            Shift_Fold_Signal(f"{src}result-shift_folded_by_n500.txt", output["time"], output["amp"])
        )

    def test_shift(self):
        src = f"{self.src}shifting/"

        signal = DigitalSignal.read(f"{src}input-shifting.txt")
        assert isinstance(signal, TimeSignal)

        output = signal.shifted(500)
        output.save(f"{src}output-shifting_by_500.txt")
        self.assertTrue(
            Shift_Fold_Signal(f"{src}result-shifting_by_500.txt", output["time"], output["amp"])
        )

        output.save(f"{src}output-shifting_by_n500.txt")
        output = signal.shifted(-500)
        self.assertTrue(
            Shift_Fold_Signal(f"{src}result-shifting_by_n500.txt", output["time"], output["amp"])
        )

    def test_deriv(self):
        self.assertTrue(DerivativeSignal())
