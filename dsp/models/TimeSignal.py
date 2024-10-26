import math
from typing import List, Sequence
from dsp.enums.graph_function import GRAPH_FUNCTION
from dsp.enums.graph_type import GRAPH_TYPE
from dsp.utils import compare_floats
from dsp.models.DigitalSignal import DigitalSignal
from dsp.enums.signal_domain import SIGNAL_DOMAIN
from matplotlib import pyplot as plt


class TimeSignal(DigitalSignal):
    def __init__(
        self,
        isPeriodic: bool,
        sample_count,
        signal_data: List[List[float]] | None = None,
    ) -> None:
        super().__init__(SIGNAL_DOMAIN.TIME, isPeriodic, sample_count, signal_data)

    def process_data(self, signal_data: List[List[float]]):
        t = signal_data[0]
        amp = signal_data[1]

        self.signal_data = (t, amp)

    def graph_wave(self, type=GRAPH_TYPE.CONTINUOUS):
        t, amp = self.signal_data

        if type == GRAPH_TYPE.DISCRETE:
            plt.plot(t, amp, "ro")

        elif type == GRAPH_TYPE.CONTINUOUS:
            plt.plot(t, amp, "b-")

        elif type == GRAPH_TYPE.BOTH_ON_PALLETE:
            plt.plot(t, amp, "ro")
            plt.plot(t, amp, "b-")

        elif type == GRAPH_TYPE.SEPARATE:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
            ax1.plot(t, amp, "ro")
            ax2.plot(t, amp, "b-")
            plt.tight_layout()

        plt.axvline(x=0, c="red", label="x=0")
        plt.axhline(y=0, c="yellow", label="y=0")
        plt.show()

    def save(self, path: str):
        with open(path, "+w") as file:
            file.write(f"{self.signal_domain.value}\n")
            file.write(f"{1 if self.isPeriodic else 0}\n")
            file.write(f"{self.sample_count}\n")

            for i in range(self.sample_count):
                file.write(f"{self.signal_data[0][i]} {self.signal_data[1][i]}\n")

    def compare(self, signal: DigitalSignal):
        if self.signal_domain != signal.signal_domain:
            raise ValueError("Signal domain must be equal")
        if self.sample_count != signal.sample_count:
            raise ValueError("Sample count must be equal")
        if self.isPeriodic != signal.isPeriodic:
            raise ValueError("Signals must be in the same periodicity")

        return all(map(compare_floats, self.signal_data[1], signal.signal_data[1]))

    def __add__(self, signal: DigitalSignal) -> "TimeSignal":
        if self.signal_domain != signal.signal_domain:
            raise ValueError("Signal domain must be equal")
        if self.sample_count != signal.sample_count:
            raise ValueError("Sample count must be equal")
        if self.isPeriodic != signal.isPeriodic:
            raise ValueError("Signals must be in the same periodicity")

        new_signal_data: List[List[float]] = list(self.signal_data)
        new_signal_data[1] = [
            new_signal_data[1][i] + signal.signal_data[1][i]
            for i in range(self.sample_count)
        ]

        return TimeSignal(self.isPeriodic, self.sample_count, new_signal_data)

    def __sub__(self, signal: DigitalSignal) -> "TimeSignal":
        if self.signal_domain != signal.signal_domain:
            raise ValueError("Signal domain must be equal")
        if self.sample_count != signal.sample_count:
            raise ValueError("Sample count must be equal")
        if self.isPeriodic != signal.isPeriodic:
            raise ValueError("Signals must be in the same periodicity")

        new_signal_data: List[List[float]] = list(self.signal_data)
        new_signal_data[1] = [
            abs(new_signal_data[1][i] - signal.signal_data[1][i])
            for i in range(self.sample_count)
        ]

        return TimeSignal(self.isPeriodic, self.sample_count, new_signal_data)

    def __mul__(self, scalar: float):
        new_signal_data = list(self.signal_data)
        new_signal_data[1] = [scalar * x for x in new_signal_data[1]]

        return TimeSignal(self.isPeriodic, self.sample_count, new_signal_data)

    def square(self):
        new_signal_data = list(self.signal_data)
        new_signal_data[1] = [x ** 2 for x in new_signal_data[1]]

        return TimeSignal(self.isPeriodic, self.sample_count, new_signal_data)

    def normalize(self):
        max_val = max([abs(x) for x in self.signal_data[1]])
        new_signal_data = [
            [self.signal_data[0][i], self.signal_data[1][i] / max_val]
            for i in range(self.sample_count)
        ]

        return TimeSignal(self.isPeriodic, self.sample_count, new_signal_data)

    def cumulative_sum(self):
        new_signal_data = [[self.signal_data[0][0]], [self.signal_data[1][0]]]
        for i in range(1, self.sample_count):
            new_signal_data[0].append(self.signal_data[0][i])
            new_signal_data[1].append(
                self.signal_data[1][i] + new_signal_data[1][i - 1]
            )

        return TimeSignal(self.isPeriodic, self.sample_count, new_signal_data)

    @staticmethod
    def generate_wave(
        function: GRAPH_FUNCTION,
        amplitude: float,
        analog_freq: float,
        sampling_freq: float,
        phase_shift: float,
        save_to: None | str = None,
        graph_type: None | GRAPH_TYPE = GRAPH_TYPE.CONTINUOUS,
    ):
        fn = math.sin if function == GRAPH_FUNCTION.SINE else math.cos

        nyquist_freq = analog_freq * 2
        if sampling_freq < nyquist_freq:
            raise ValueError(
                f"Sample frequency must be greater than or equal to Nyquist Frequency ({nyquist_freq})"
            )

        sample_count = int(sampling_freq)
        n = [float(i) for i in range(sample_count)]
        amp = [
            amplitude * fn(2 * math.pi * analog_freq / sampling_freq * i + phase_shift)
            for i in n
        ]

        signal = TimeSignal(False, sample_count, [n, amp])

        if save_to:
            signal.save(save_to)
        if graph_type:
            signal.graph_wave(graph_type)

        return signal
