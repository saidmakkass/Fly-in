from typing import List, Tuple

from .constants import ZONE_RADIUS


class Scaler:
    def __init__(self, xs: List[int], ys: List[int], width: int, height: int):
        self.min_x = min(xs)
        self.min_y = min(ys)
        self.max_x = max(xs)
        self.max_y = max(ys)

        self.zoom = 1.0
        self.ox = 0
        self.oy = 0

        self.span_x = (self.max_x - self.min_x) or 1.0
        self.span_y = (self.max_y - self.min_y) or 1.0

        self.pad = ZONE_RADIUS * 2
        self.resize(width, height)

    def resize(self, width: int, height: int) -> None:
        self.width = width - self.pad * 2
        self.height = height - self.pad * 2

    def scale(self, x: int, y: int, pad: bool = True) -> Tuple[float, float]:
        frac_x = (x - self.min_x) / self.span_x
        frac_y = (y - self.min_y) / self.span_y
        if pad:
            return (
                frac_x * self.width * self.zoom + self.ox + self.pad,
                frac_y * self.height* self.zoom + self.oy + self.pad,
            )
        return (
            frac_x * self.width * self.zoom + self.ox,
            frac_y * self.height* self.zoom + self.oy,
        )
