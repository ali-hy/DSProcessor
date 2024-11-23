import cmath
import math
from typing import Any, List, Sequence, Tuple

from matplotlib.figure import Figure
from dsp.enums.graph_type import GRAPH_TYPE
from dsp.enums.signal_domain import SIGNAL_DOMAIN
from dsp.utils import compare_floats


class DigitalSignal:
    def __init__(
        self,
        signal_domain: SIGNAL_DOMAIN,
        is_periodic: bool,
        sample_count: int,
        signal_data: List[List[float]] | None = None,
    ) -> None:
        self.signal_domain = signal_domain
        self.is_periodic = is_periodic
        self.sample_count = sample_count

        if signal_data:
            self.process_data(signal_data)

    def compare(self, signal: "DigitalSignal"):
        if self.signal_domain != signal.signal_domain:
            raise ValueError("Signal domain must be equal")
        if self.sample_count != signal.sample_count:
            raise ValueError("Sample count must be equal")
        if self.is_periodic != signal.is_periodic:
            raise ValueError("Periodicity must be equal")

        for _ in range(len(self.signal_data)):
            if not all(map(compare_floats, self.signal_data[1], signal.signal_data[1])):
                return False

        return True

    def __add__(self, signal: "DigitalSignal"):
        raise NotImplementedError

    def __sub__(self, signal: "DigitalSignal"):
        raise NotImplementedError

    def __mul__(self, scalar: float):
        raise NotImplementedError

    def square(self):
        raise NotImplementedError

    def normalize(self):
        raise NotImplementedError

    def cumulative_sum(self):
        raise NotImplementedError

    def process_data(self, signal_data: List[List[float]]):
        self.signal_data = list(signal_data)

    def graph_wave(self, type=GRAPH_TYPE.CONTINUOUS, parent: Figure | None = None):
        raise NotImplementedError

    def quantize_w_levels(self, level_count: int, save_path: str | None = None):
        raise NotImplementedError

    def quantize_w_bits(self, bit_count: int, save_path: str | None = None):
        raise NotImplementedError

    def switch_domain(self, sampling_freq: float | None = None):
        """
        Compute the Discrete Fourier Transform (DFT) of the signal.
        """

        inverse = self.signal_domain == SIGNAL_DOMAIN.FREQUENCY

        if inverse:
            assert isinstance(self, FrequencySignal)
            assert sampling_freq is not None
            _, amp, pshift = self.signal_data
            data = [
                amp[i] * cmath.exp(1j * pshift[i]) for i in range(self.sample_count)
            ]
        else:
            assert isinstance(self, TimeSignal)
            _, data = self.signal_data

        assert data
        N = len(data)
        dft_result: List[complex] = []

        for k in range(N):
            # Compute the k-th frequency component
            X_k = 0
            for n in range(N):
                angle = -2 * math.pi * k * n / N

                if inverse:
                    angle *= -1

                X_k += data[n] * cmath.exp(1j * angle)  # e^(-j * angle)

            if inverse:
                X_k /= N
            dft_result.append(X_k)

        return (
            TimeSignal(
                self.is_periodic,
                N,
                signal_data=[list(range(N)), [x.real for x in dft_result]],
            )
            if inverse
            else FrequencySignal(
                self.is_periodic, N, harmonics=dft_result, sample_freq=sampling_freq
            )
        )

    @staticmethod
    def read(path: str | None):
        if (not path):
            raise ValueError("Path must be provided")

        with open(path, "r") as file:
            signalDomain = int(file.readline())
            isPeriodic = int(file.readline()) == 1
            nSamples = int(file.readline())

            signal_data: List[List[float]] = []

            if signalDomain == SIGNAL_DOMAIN.TIME.value:
                signal_data = [[], []]
            else:
                signal_data = [[], [], []]

            for line in file:
                line = line.strip()
                record = line.split(" ")

                for i in range(len(record)):
                    signal_data[-i - 1].append(float(record[-i - 1]))

            return (
                TimeSignal(isPeriodic, nSamples, signal_data)
                if signalDomain == SIGNAL_DOMAIN.TIME.value
                else FrequencySignal(isPeriodic, nSamples, signal_data)
            )

    def save(self, path: str, data: List[List[Any]] | None = None):
        with open(path, "+w") as file:
            file.write(f"{self.signal_domain.value}\n")
            file.write(f"{1 if self.is_periodic else 0}\n")
            file.write(f"{self.sample_count}\n")

            if not data:
                data = self.signal_data

            for i in range(self.sample_count):
                line = " ".join(
                    [str(x) for x in [data[j][i] for j in range(len(data))]]
                )
                file.write(f"{line}\n")


from dsp.models.TimeSignal import TimeSignal
from dsp.models.FrequencySignal import FrequencySignal
