"""

"""

import math
from typing import Callable


class Window:
    def __init__(self, fn: Callable[[int, int], float], stopbandAttenuation: float, transitionWidthFactor: float, name: str | None = None) -> None:
        self.fn = fn
        self.stopband_attenuation = stopbandAttenuation
        self.transitionWidthFactor = transitionWidthFactor
        self.name = name

    def getCoefficientCount(self, transitionBand: float):
        val = math.ceil(self.transitionWidthFactor / transitionBand)
        res = int(val) if val == int(val) else int(val) + 1
        res = res + 1 if res % 2 == 0 else res
        print(f"Coefficient count ({self.transitionWidthFactor}/{transitionBand}): ", res)
        return res
