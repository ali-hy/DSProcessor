from typing import List, Tuple
from dsp.enums.graph_type import GRAPH_TYPE
from dsp.enums.signal_domain import SIGNAL_DOMAIN


class DigitalSignal:
    def __init__(self, signal_domain: SIGNAL_DOMAIN, isPeriodic: bool, sample_count, signal_data: List[List[float]] | None = None ) -> None:
        self.signal_domain = signal_domain
        self.isPeriodic = isPeriodic
        self.sample_count = sample_count

        if signal_data:
            self.process_data(signal_data)

    def process_data(self, signal_data: List[List[float]]):
        self.signal_data = tuple(signal_data)

    def graph_wave(self, type=GRAPH_TYPE.CONTINUOUS):
        raise NotImplementedError

    @staticmethod
    def read(path: str):
        with open(path, 'r') as file:
            signalDomain = int(file.readline())
            isPeriodic = int(file.readline()) == 1
            nSamples = int(file.readline())

            signal_data: List[List[float]] = []

            if (signalDomain == SIGNAL_DOMAIN.TIME.value):
                signal_data = [[], []]
            else:
                signal_data = [[], [], []]

            for line in file:
                line = line.strip(' ')
                line = line.strip('\n')
                record = line.split(' ')

                for i in range(len(record)):
                    signal_data[i].append(float(record[i]))

            return TimeSignal(isPeriodic, nSamples, signal_data) if signalDomain == SIGNAL_DOMAIN.TIME.value\
                else FrequencySignal(isPeriodic, nSamples, signal_data)

    def save(self, path: str):
        raise NotImplementedError

from dsp.models.TimeSignal import TimeSignal
from dsp.models.FrequencySignal import FrequencySignal
