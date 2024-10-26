from typing import List
from dsp.models.DigitalSignal import DigitalSignal
from dsp.enums.signal_domain import SIGNAL_DOMAIN

class FrequencySignal(DigitalSignal):
    def __init__(self, isPeriodic: bool, sample_count: int, signal_data: List[List[float]]) -> None:
        super().__init__(SIGNAL_DOMAIN.FREQUENCY, isPeriodic, sample_count, signal_data)

    def process_data(self, signal_data: List[List[int]]):
        self.signal_data = signal_data

    def graph_wave(self, type=1):
        pass
