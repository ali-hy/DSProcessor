import math
from typing import Any, List, Sequence, Type, Union

from matplotlib.axes import Axes
from dsp.enums.graph_function import GRAPH_FUNCTION
from dsp.enums.graph_type import GRAPH_TYPE
from dsp.utils import compare_floats
from dsp.models.DigitalSignal import DigitalSignal
from dsp.enums.signal_domain import SIGNAL_DOMAIN
from matplotlib import pyplot as plt
from matplotlib.figure import Figure


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

    def graph_wave(self, type=GRAPH_TYPE.CONTINUOUS, parent: Figure | None = None):
        plot_on: Axes | None = None

        if parent:
            figure = parent
            plot_on = figure.subplots()
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

    def save(self, path: str, data: List[List[Any]] | None = None):
        with open(path, "+w") as file:
            file.write(f"{self.signal_domain.value}\n")
            file.write(f"{1 if self.isPeriodic else 0}\n")
            file.write(f"{self.sample_count}\n")

            if data:
                for i in range(self.sample_count):
                    line = " ".join(
                        [str(x) for x in [data[j][i] for j in range(len(data))]]
                    )
                    file.write(f"{line}\n")
            else:
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

        new_signal_data: List[List[float]] = [list(arr) for arr in self.signal_data]

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

        new_signal_data: List[List[float]] = [list(arr) for arr in self.signal_data]

        new_signal_data[1] = [
            abs(new_signal_data[1][i] - signal.signal_data[1][i])
            for i in range(self.sample_count)
        ]

        return TimeSignal(self.isPeriodic, self.sample_count, new_signal_data)

    def __mul__(self, scalar: float):
        new_signal_data: List[List[float]] = [list(arr) for arr in self.signal_data]
        new_signal_data[1] = [scalar * x for x in new_signal_data[1]]

        return TimeSignal(self.isPeriodic, self.sample_count, new_signal_data)

    def square(self):
        new_signal_data = list(self.signal_data)
        new_signal_data[1] = [x**2 for x in new_signal_data[1]]

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
                    return i, level_midpoints[i] # level, midpoint
            return i+1, level_midpoints[-1]

        res: List[List[str | int | float]] = [[], []]
        # res[0] -> binary representation of level
        # res[1] -> midpoint value mapped to level

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

        level_midpoints = [
            (levels[i] + levels[i + 1]) / 2 for i in range(level_count)
        ]

        def find_level(x: float):
            for i in range(level_count - 1):
                if levels[i] <= x < levels[i + 1]:
                    return i, level_midpoints[i]

            return i+1, level_midpoints[-1]

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
