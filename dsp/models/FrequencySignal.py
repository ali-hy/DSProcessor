import math
from typing import Any, List, Literal, Union

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from dsp.enums.graph_type import GRAPH_TYPE
from dsp.models.DigitalSignal import DigitalSignal
from dsp.enums.signal_domain import SIGNAL_DOMAIN


class FrequencySignal(DigitalSignal):
    axes = {
        "freq": 0,
        "amp": 1,
        "pshift": 2,
    }

    def __init__(
        self,
        is_periodic: bool,
        sample_count: int,
        signal_data: List[List[float]] | None = None,
        harmonics: List[complex] | None = None,
        sample_freq: float | None = None,
    ) -> None:
        super().__init__(
            SIGNAL_DOMAIN.FREQUENCY, is_periodic, sample_count, signal_data
        )
        self.harmonics = harmonics
        if self.harmonics:
            self.set_data_from_harmonics(sample_freq or sample_count)

    def set_data_from_harmonics(self, sample_freq: float):
        assert self.harmonics is not None

        def get_amp(h: complex):
            return math.sqrt(h.real**2 + h.imag**2)

        def get_pshift(h: complex):
            return math.atan2(h.imag, h.real)

        sample_preiod = 1 / sample_freq
        omega = (2 * math.pi) / (self.sample_count * sample_preiod)

        f = [omega * i for i in range(1, self.sample_count + 1)]
        amp = [get_amp(h) for h in self.harmonics]
        pshift = [get_pshift(h) for h in self.harmonics]

        self.signal_data = [f, amp, pshift]

    def __getitem__(self, name: Literal["freq", "amp", "pshift"]) -> Any:
        return self.signal_data[FrequencySignal.axes[name]]

    def process_data(self, signal_data: List[List[int]]):
        self.signal_data = signal_data
        while len(self.signal_data) < 3:
            self.signal_data.append([0] * self.sample_count)

    def remove_dc(self):
        if self.harmonics is not None:
            new_harmonics = list(self.harmonics)
            new_harmonics[0] = 0
            new_signal = FrequencySignal(
                self.is_periodic, self.sample_count, harmonics=new_harmonics
            )
        # else:
        #     new_signal_data = [list(data) for data in self.signal_data]
        #     new_signal_data[1][0] = 0
        #     new_signal = FrequencySignal(
        #         self.is_periodic, self.sample_count
        #     )

        return new_signal

    def conjugate(self):
        assert self.harmonics is not None

        new_harmonics = [h.conjugate() for h in self.harmonics]
        return FrequencySignal(
            self.is_periodic, self.sample_count, harmonics=new_harmonics
        )

    def graph_wave(self, type=GRAPH_TYPE.DISCRETE, parent: Figure | None = None):
        plot_on: Axes | None = None

        if parent:
            figure = parent
            plot_on = figure.subplots()
        else:
            figure = plt.figure()
            plot_on = figure.add_subplot(111)

        f, amp, pshift = self.signal_data

        if type == GRAPH_TYPE.DISCRETE:
            plot_on.plot(f, amp, "bo")
            plot_on.plot(f, pshift, "go")

        elif type == GRAPH_TYPE.CONTINUOUS:
            plot_on.plot(f, amp, "b-")
            plot_on.plot(f, pshift, "g-")

        elif type == GRAPH_TYPE.BOTH_ON_PALLETE:
            plot_on.plot(f, amp, "ro")
            plot_on.plot(f, amp, "b-")

        elif type == GRAPH_TYPE.SEPARATE:
            ax1, ax2 = figure.subplots(1, 2)

            ax1.plot(f, amp, "ro")
            ax2.plot(f, amp, "b-")
            figure.tight_layout()

        plot_on.axvline(x=0, c="red", label="x=0")
        plot_on.axhline(y=0, c="yellow", label="y=0")

        if figure is plt:
            assert not isinstance(figure, Figure)
            figure.show()

    def __mul__(self, factor: "float | FrequencySignal") -> "FrequencySignal":
        assert self.harmonics is not None

        print("\nharmonics", self.harmonics)

        if isinstance(factor, float):
            new_harmonics = [h * factor for h in self.harmonics]
        elif isinstance(factor, FrequencySignal):
            assert factor.harmonics is not None
            print("factor harmonicx", factor.harmonics)
            new_harmonics = [h1 * h2 for h1, h2 in zip(self.harmonics, factor.harmonics)]
        else:
            raise TypeError("Unsupported type for multiplication of FrequencySignal")

        print("new harmonics", new_harmonics)

        return FrequencySignal(
            self.is_periodic, self.sample_count, harmonics=new_harmonics
        )
