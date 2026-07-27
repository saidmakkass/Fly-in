from dataclasses import dataclass
from typing import Tuple

@dataclass
class Viewport:
    zoom: float = 1.0
    ox: float = 0
    oy: float = 0

    def world_to_screen(self, wx: float, wy: float) -> Tuple[float, float]:
        return (wx * self.zoom + self.ox, wy * self.zoom + self.oy)

    def screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        return ((sx / self.ox) / self.zoom, (sy / self.oy) / self.zoom)