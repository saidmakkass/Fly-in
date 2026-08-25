from typing import List, Tuple

from .constants import ZONE_RADIUS


class Scaler:
    """Scale and pan map coordinates to pixel positions for the visualizer."""
    def __init__(self, xs: List[int], ys: List[int], width: int, height: int):
        """Compute bounds and initialize scaler with widget dimensions."""
        self.min_x = min(xs)
        self.min_y = min(ys)
        self.max_x = max(xs)
        self.max_y = max(ys)

        self.span_x = (self.max_x - self.min_x) or 1.0
        self.span_y = (self.max_y - self.min_y) or 1.0

        self.pad = ZONE_RADIUS * 2
        self.resize(width, height)
        self.reset()

    def reset(self) -> None:
        """Reset pan/zoom to defaults."""
        self.zoom = 1.0
        self.ox = 0.0
        self.oy = 0.0

    def resize(self, width: int, height: int) -> None:
        """Update available drawing area after a window resize."""
        self.width = width - self.pad * 2
        self.height = height - self.pad * 2

    def scale(self, x: int, y: int) -> Tuple[float, float]:
        """Return scaled pixel coordinates for logical (x, y)."""
        frac_x = (x - self.min_x) / self.span_x
        frac_y = (y - self.min_y) / self.span_y
        return (
            frac_x * self.width * self.zoom + self.ox + self.pad,
            frac_y * self.height * self.zoom + self.oy + self.pad,
        )
