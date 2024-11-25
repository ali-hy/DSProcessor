import math
from typing import Any, List, Literal

from matplotlib.axes import Axes
from dsp.enums.graph_function import GRAPH_FUNCTION
from dsp.enums.graph_type import GRAPH_TYPE
from dsp.models.FrequencySignal import FrequencySignal
from dsp.utils import compare_floats
from dsp.models.DigitalSignal import DigitalSignal
from dsp.enums.signal_domain import SIGNAL_DOMAIN
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

import cmath


class TimeSignal(DigitalSignal):
    axes = {
        "time": 0,
        "amp": 1,
    }

    def __init__(
        self,
        isPeriodic: bool,
        sample_count: int,
        signal_data: List[List[float]] | None = None,
    ) -> None:
        super().__init__(SIGNAL_DOMAIN.TIME, isPeriodic, sample_count, signal_data)

    def process_data(self, signal_data: List[List[float]]):
        t = signal_data[0]
        amp = signal_data[1]

        self.signal_data = [t, amp]

    def graph_wave(self, type=GRAPH_TYPE.CONTINUOUS, parent: Figure | None = None):
        plot_on: Axes | None = None

        if parent:
            figure = parent
            plot_on = figure.subplots()
            plot_on.remove()
            plot_on = figure.add_subplot()
        else:
            figure = plt.figure()
            plot_on = figure.add_subplot(111)

        t, amp = self.signal_data

        if type == GRAPH_TYPE.DISCRETE:
            plot_on.plot(t, amp, "ro")

        elif type == GRAPH_TYPE.CONTINUOUS:
            plot_on.plot(t, amp, "b-")

        elif type == GRAPH_TYPE.BOTH_ON_PALLETE:
            plot_on.plot(t, amp, "ro")
            plot_on.plot(t, amp, "b-")

        elif type == GRAPH_TYPE.SEPARATE:
            ax1, ax2 = figure.subfigures(2, 1)

            ax1.plot(t, amp, "ro")
            ax2.plot(t, amp, "b-")
            figure.tight_layout()

        plot_on.axvline(x=0, c="red", label="x=0")
        plot_on.axhline(y=0, c="yellow", label="y=0")

        if figure is plt:
            assert not isinstance(figure, Figure)
            figure.show()

    def compare(self, signal: DigitalSignal):
        if self.signal_domain != signal.signal_domain:
            raise ValueError("Signal domain must be equal")
        if self.sample_count != signal.sample_count:
            raise ValueError("Sample count must be equal")
        if self.is_periodic != signal.is_periodic:
            raise ValueError("Signals must be in the same periodicity")

        return all(map(compare_floats, self.signal_data[1], signal.signal_data[1]))

    @staticmethod
    def match_signal_lengths(signal1: "TimeSignal", signal2: "TimeSignal"):
        """
        This method extends the signal with the shorter length to match the length of the signal with the longer length
        This method modifies the signal(s) in place

        Assumption: Delta time is always 1
        """

        signal1_copy = TimeSignal(
            signal1.is_periodic,
            signal1.sample_count,
            [list(x) for x in signal1.signal_data],
        )
        signal2_copy = TimeSignal(
            signal2.is_periodic,
            signal2.sample_count,
            [list(x) for x in signal2.signal_data],
        )

        # Figure out which signal starts first
        early_signal = None
        late_signal = None

        if signal1_copy["time"][0] < signal2_copy["time"][0]:
            early_signal = signal1_copy
            late_signal = signal2_copy
        elif signal2_copy["time"][0] < signal1_copy["time"][0]:
            early_signal = signal2_copy
            late_signal = signal1_copy

        # Figure out which signal ends first
        end_early_signal = None
        end_late_signal = None

        if signal1_copy["time"][-1] < signal2_copy["time"][-1]:
            end_early_signal = signal1_copy
            end_late_signal = signal2_copy
        elif signal2_copy["time"][-1] < signal1_copy["time"][-1]:
            end_early_signal = signal2_copy
            end_late_signal = signal1_copy

        # Extend the signal that starts first to match the length of the signal that ends first
        if early_signal and late_signal:
            early_signal_data = early_signal.signal_data
            late_signal_data = late_signal.signal_data

            missing_samples = int(late_signal_data[0][0] - early_signal_data[0][0])

            late_signal_pos = early_signal_data[0].index(late_signal_data[0][0])
            late_signal_data[0] = (
                early_signal_data[0][:late_signal_pos] + late_signal_data[0]
            )

            extension = [0.0] * missing_samples
            if late_signal.is_periodic:

                for i in range(-1, -len(extension) - 1, -1):
                    extension[i] = late_signal_data[1][i]

            late_signal_data[1] = extension + late_signal_data[1]

            late_signal.signal_data = late_signal_data

        # Extend the signal that ends first to match the length of the signal that starts first
        if end_early_signal and end_late_signal:
            end_early_signal_data = end_early_signal.signal_data
            end_late_signal_data = end_late_signal.signal_data

            missing_samples = int(
                end_late_signal_data[0][-1] - end_early_signal_data[0][-1]
            )

            end_early_signal_pos = end_late_signal_data[0].index(
                end_early_signal_data[0][-1]
            )
            end_early_signal_data[0] = (
                end_early_signal_data[0]
                + end_late_signal_data[0][end_early_signal_pos + 1 :]
            )

            extension = [0.0] * missing_samples
            if end_early_signal.is_periodic:

                for i in range(-1, -len(extension) - 1, -1):
                    extension[i] = end_early_signal_data[1][i]

            end_early_signal_data[1] = end_early_signal_data[1] + extension
            end_early_signal.signal_data = end_early_signal_data

        return signal1_copy, signal2_copy

    def __add__(self, signal: DigitalSignal) -> "TimeSignal":
        if self.signal_domain != signal.signal_domain or not isinstance(
            signal, TimeSignal
        ):
            raise ValueError("Signal domain must be equal")

        sig1, sig2 = TimeSignal.match_signal_lengths(self, signal)
        assert len(sig1) == len(sig2)

        new_signal_data: List[List[float]] = [list(arr) for arr in sig1.signal_data]

        new_signal_data[1] = [
            new_signal_data[1][i] + sig2.signal_data[1][i] for i in range(len(sig1))
        ]

        return TimeSignal(
            self.is_periodic and signal.is_periodic, len(self), new_signal_data
        )

    def __sub__(self, signal: DigitalSignal) -> "TimeSignal":
        if self.signal_domain != signal.signal_domain or not isinstance(
            signal, TimeSignal
        ):
            raise ValueError("Signal domain must be equal")

        sig1, sig2 = TimeSignal.match_signal_lengths(self, signal)
        assert len(sig1) == len(sig2)

        new_signal_data: List[List[float]] = [list(arr) for arr in sig1.signal_data]

        new_signal_data[1] = [
            abs(new_signal_data[1][i] - sig2.signal_data[1][i])
            for i in range(len(sig1))
        ]

        return TimeSignal(
            self.is_periodic and signal.is_periodic, len(self), new_signal_data
        )

    def __mul__(self, scalar: float):
        new_signal_data: List[List[float]] = [list(arr) for arr in self.signal_data]
        new_signal_data[1] = [scalar * x for x in new_signal_data[1]]

        return TimeSignal(self.is_periodic, self.sample_count, new_signal_data)

    def square(self):
        new_signal_data = list(self.signal_data)

        # mupltiply each x in the amplitude by itself
        new_signal_data[1] = [x**2 for x in self["amp"]]

        return TimeSignal(self.is_periodic, self.sample_count, new_signal_data)

    def normalize(self):
        max_val = max([abs(x) for x in self.signal_data[1]])
        new_signal_data = [
            [self.signal_data[0][i], self.signal_data[1][i] / max_val]
            for i in range(self.sample_count)
        ]

        return TimeSignal(self.is_periodic, self.sample_count, new_signal_data)

    def cumulative_sum(self):
        new_signal_data = [[self.signal_data[0][0]], [self.signal_data[1][0]]]
        for i in range(1, self.sample_count):
            new_signal_data[0].append(self.signal_data[0][i])
            new_signal_data[1].append(
                self.signal_data[1][i] + new_signal_data[1][i - 1]
            )

        return TimeSignal(self.is_periodic, self.sample_count, new_signal_data)

    def quantize_w_bits(self, bit_count: int, save_path: str | None = None):
        max_val = max(self.signal_data[1])
        min_val = min(self.signal_data[1])

        level_count = 2**bit_count
        step = (max_val - min_val) / level_count

        levels = [min_val + step * i for i in range(level_count + 1)]
        level_midpoints = [(levels[i] + levels[i + 1]) / 2 for i in range(level_count)]

        def find_level(x: float):
            for i in range(level_count - 1):
                if levels[i] <= x < levels[i + 1]:
                    return i, level_midpoints[i]  # level, midpoint
            return i + 1, level_midpoints[-1]

        res: List[List[str | int | float]] = [[], []]

        for i in range(self.sample_count):
            level, midpoint = find_level(self.signal_data[1][i])
            res[0].append(f"{level:0{bit_count}b}")
            res[1].append(midpoint)

        if save_path:
            self.save(save_path, res)

        return res

    def quantize_w_levels(self, level_count: int, save_path: str | None = None):
        max_val = max(self.signal_data[1])
        min_val = min(self.signal_data[1])

        bit_count = math.ceil(math.log2(level_count))

        step = (max_val - min_val) / level_count
        levels = [min_val + step * i for i in range(level_count + 1)]

        level_midpoints = [(levels[i] + levels[i + 1]) / 2 for i in range(level_count)]

        def find_level(x: float):
            for i in range(level_count - 1):
                if levels[i] <= x < levels[i + 1]:
                    return i, level_midpoints[i]

            return i + 1, level_midpoints[-1]

        res: List[List[str | float]] = [[], [], [], []]

        for i in range(self.sample_count):
            level, midpoint = find_level(self.signal_data[1][i])
            res[0].append(level + 1)
            res[1].append(f"{level:>0{bit_count}b}")
            res[2].append(midpoint)
            res[3].append(midpoint - self.signal_data[1][i])

        if save_path:
            self.save(save_path, res)

        return res

    def dct(self, sampling_frequency: float = 1.0):
        """
        Applies Discrete Cosine Transform to the signal data

        @param sampling_frequency: Sampling frequency of the signal
        @type sampling_frequency: float
        @default: 1.0 - uses a normalized value given that the sampling frequency isn't provided
        """

        N = self.sample_count
        dct_coefficients = [math.sqrt(2 / N)] * N

        for k in range(N):
            yk = 0.0
            for n in range(N):
                yk += self.signal_data[1][n] * math.cos(
                    (math.pi / (4 * N)) * (2 * n - 1) * (2 * k - 1)
                )

            dct_coefficients[k] *= yk

        frequencies = [0.5 * k * sampling_frequency / N for k in range(N)]

        return FrequencySignal(self.is_periodic, N, [frequencies, dct_coefficients])

    def shifted(self, shift_amount: int):
        new_signal_data = [list(x) for x in self.signal_data]

        for i in range(len(self)):
            new_signal_data[0][i] -= shift_amount

        return TimeSignal(self.is_periodic, self.sample_count, new_signal_data)

    def folded(self):
        new_signal_data = [list(x) for x in self.signal_data]

        new_signal_data[0] = sorted([-x for x in new_signal_data[0]])

        for i in range(len(self)):
            new_signal_data[1][i] = self.signal_data[1][-i - 1]

        return TimeSignal(self.is_periodic, self.sample_count, new_signal_data)

    def first_derivative(self):
        return self - self.shifted(-1)

    def second_derivative(self):
        return self.shifted(-1) + self.shifted(1) - (self * 2)

    def __getitem__(self, name: Literal["time", "amp"]) -> Any:
        return self.signal_data[TimeSignal.axes[name]]

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
