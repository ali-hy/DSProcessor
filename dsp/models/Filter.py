"""
Filter module

Contains a Filter class that is used to filter signals.
Filter class represents FIR filters, as we will not be implementing IIR filters.
"""

import math
from typing import Tuple
from dsp.enums.filter_type import FILTER_TYPE
from dsp.models import TimeSignal
from dsp.models.Window import Window


class FirFilter:
    def __init__(
        self,
        filter_type: FILTER_TYPE,
        sampling_frequency: int,
        stopband_attenuation: float,
        transition_band: float,
        cutoff: float | None = None,
        highcutoff: float | None = None,
        lowcutoff: float | None = None,
    ) -> None:
        # define specifications
        self.sampling_frequency = sampling_frequency
        self.filter_type = filter_type
        self.stopband_attenuation = stopband_attenuation
        self.transition_band = transition_band

        self.use_single_cutoff = filter_type in (FILTER_TYPE.LOW_PASS, FILTER_TYPE.HIGH_PASS)
        self.use_double_cutoff = filter_type in (FILTER_TYPE.BAND_PASS, FILTER_TYPE.BAND_STOP)

        if self.use_single_cutoff:
            self.cutoff = cutoff
        elif self.use_double_cutoff:
            self.lowcutoff = lowcutoff
            self.highcutoff = highcutoff

        # Normalize transition band
        self.transition_band = self.transition_band / self.sampling_frequency

        # get window
        self.window = self.getWindow()
        self.coefficient_count = self.window.getCoefficientCount(self.transition_band)

        # Normalize cutoff frequencies
        if self.use_single_cutoff and self.cutoff is not None:
            self.cutoff = self.cutoff / self.sampling_frequency
        if self.use_double_cutoff:
            if self.lowcutoff is not None:
                self.lowcutoff = self.lowcutoff / self.sampling_frequency
            if self.highcutoff is not None:
                self.highcutoff = self.highcutoff / self.sampling_frequency

        if self.filter_type == FILTER_TYPE.LOW_PASS:
            assert self.cutoff is not None
            print("Cut off frequency (not shifted): ", self.cutoff)
            print("Transition band: ", self.transition_band)
            self.wc = self.cutoff + self.transition_band / 2
            print("Cut off frequency: ", self.wc)
        elif self.filter_type == FILTER_TYPE.HIGH_PASS:
            assert self.cutoff is not None
            self.wc = self.cutoff - self.transition_band / 2
        elif self.filter_type == FILTER_TYPE.BAND_PASS:
            assert self.lowcutoff is not None and self.highcutoff is not None
            self.wc1 = self.lowcutoff - self.transition_band / 2
            self.wc2 = self.highcutoff + self.transition_band / 2
        elif self.filter_type == FILTER_TYPE.BAND_STOP:
            assert self.lowcutoff is not None and self.highcutoff is not None
            self.wc1 = self.lowcutoff + self.transition_band / 2
            self.wc2 = self.highcutoff - self.transition_band / 2

        # get filter
        self.hD = self.get_filter()
        N = self.coefficient_count
        m = (N - 1) // 2
        d_hd = [self.hD(n) for n in range(-m, m + 1)]
        print("---------\nhD(n)\n-----------", d_hd)
        d_window = [self.window.fn(n, N) for n in range(-m, m + 1)]
        print("---------\nwindow(n)\n-----------", d_window)
        self.coefficients = [d_hd[n] * d_window[n] for n in range(0, m + 1)]
        self.coefficients = self.coefficients + list(reversed(self.coefficients[:-1]))

        print("---------\ffilter(n)\n-----------")
        print(self.coefficients)

    def to_signal(self) -> TimeSignal:
        N = self.coefficient_count
        m = (N - 1) // 2
        return TimeSignal(is_periodic=False, sample_count=self.coefficient_count, signal_data=[
            [x for x in range(-m, m + 1)],
            [*self.coefficients]
        ])

    def apply(self, signal: TimeSignal) -> TimeSignal:
        """
        Apply the filter on the input signal x
        """

        return signal.convolve(
            self.to_signal()
        )

    # region: Windows
    def getWindow(self):
        for window in self.windows:
            if window.stopband_attenuation >= self.stopband_attenuation:
                print(f"Using {window.name} window")
                return window

        raise ValueError("No window found for the given stopband attenuation")

    rectangularWindow = Window(
        fn=lambda n, N: 1, stopbandAttenuation=21, transitionWidthFactor=0.9, name="Rectangular"
    )
    hanningWindow = Window(
        fn=lambda n, N: 0.5 + 0.5 * math.cos(2 * math.pi * n / N),
        stopbandAttenuation=44,
        transitionWidthFactor=3.1,
        name="Hanning",
    )
    hammingWindow = Window(
        fn=lambda n, N: 0.54 + 0.46 * math.cos(2 * math.pi * n / N),
        stopbandAttenuation=53,
        transitionWidthFactor=3.3,
        name="Hamming",
    )
    blackmanWindow = Window(
        fn=lambda n, N: 0.42
        + 0.5 * math.cos(2 * math.pi * n / (N - 1))
        + 0.08 * math.cos(4 * math.pi * n / (N - 1)),
        stopbandAttenuation=74,
        transitionWidthFactor=5.5,
        name="Blackman",
    )

    windows = sorted([
        rectangularWindow,
        hanningWindow,
        hammingWindow,
        blackmanWindow,
    ], key=lambda x: x.stopband_attenuation)
    # endregion

    # region: Filters
    def get_filter(self):
        if self.filter_type == FILTER_TYPE.LOW_PASS:
            return self.low_pass_filter()
        elif self.filter_type == FILTER_TYPE.HIGH_PASS:
            return self.high_pass_filter()
        elif self.filter_type == FILTER_TYPE.BAND_PASS:
            return self.band_pass_filter()
        elif self.filter_type == FILTER_TYPE.BAND_STOP:
            return self.band_stop_filter()
        else:
            raise ValueError("Invalid filter type")

    def low_pass_filter(self):
        if self.filter_type != FILTER_TYPE.LOW_PASS:
            raise ValueError("Filter type must be LOW_PASS")
        if self.wc is None:
            raise ValueError("Cutoff frequency must be provided for low pass filter")

        def fn(n: int) -> float:
            assert self.wc is not None
            return (
                self.wc * 2
                if n == 0
                else math.sin(2 * math.pi * self.wc * n) / (math.pi * n)
            )

        return fn

    def high_pass_filter(self):
        if self.filter_type != FILTER_TYPE.HIGH_PASS:
            raise ValueError("Filter type must be HIGH_PASS")
        if self.wc is None:
            raise ValueError("Cutoff frequency must be provided for high pass filter")

        def fn(n: int) -> float:
            assert self.wc is not None
            return (
                -self.wc * 2
                if n == 0
                else math.sin(2 * math.pi * self.wc * n)
                / (math.pi * n)
            )

        return fn

    def band_pass_filter(self):
        if self.filter_type != FILTER_TYPE.BAND_PASS:
            raise ValueError("Filter type must be BAND_PASS")
        if self.wc1 is None or self.wc2 is None:
            raise ValueError("Low and high cutoff frequencies must be provided")

        def fn(n: int) -> float:
            assert self.wc1 is not None and self.wc2 is not None
            return (
                (self.wc2 - self.wc1) * 2
                if n == 0
                else (
                    math.sin(2 * math.pi * self.wc2 * n)
                    / (math.pi * n)
                    - math.sin(2 * math.pi * self.wc1 * n)
                    / (math.pi * n)
                )
            )

        return fn

    def band_stop_filter(self):
        if self.filter_type != FILTER_TYPE.BAND_STOP:
            raise ValueError("Filter type must be BAND_STOP")
        if self.wc2 is None or self.wc1 is None:
            raise ValueError("Low and high cutoff frequencies must be provided")

        def fn(n: int) -> float:
            assert self.wc1 is not None and self.wc2 is not None
            return (
                -((self.wc2 - self.wc1) * 2)
                if n == 0
                else (
                    math.sin(2 * math.pi * self.wc1 * n)
                    / (math.pi * n)
                    - math.sin(2 * math.pi * self.wc2 * n)
                    / (math.pi * n)
                )
            )

        return fn
    # endregion
