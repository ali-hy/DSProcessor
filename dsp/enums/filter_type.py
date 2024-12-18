from enum import Enum

class FILTER_TYPE(Enum):
    LOW_PASS = 0
    HIGH_PASS = 1
    BAND_PASS = 2
    BAND_STOP = 3
