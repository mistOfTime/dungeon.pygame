# Eclipse Depths - Timer utility

from __future__ import annotations


class Timer:
    """Countdown timer. Call update(dt) each frame."""

    def __init__(self, duration: float, auto_reset: bool = False) -> None:
        self.duration   = duration
        self.auto_reset = auto_reset
        self._elapsed   = duration   # start "done"
        self.active     = False

    def start(self) -> None:
        self._elapsed = 0.0
        self.active   = True

    def reset(self) -> None:
        self.start()

    def update(self, dt: float) -> None:
        if self.active:
            self._elapsed += dt
            if self._elapsed >= self.duration:
                if self.auto_reset:
                    self._elapsed -= self.duration
                else:
                    self._elapsed = self.duration
                    self.active   = False

    @property
    def done(self) -> bool:
        return self._elapsed >= self.duration

    @property
    def progress(self) -> float:
        """0.0 _ 1.0"""
        return min(1.0, self._elapsed / self.duration) if self.duration else 1.0

    @property
    def remaining(self) -> float:
        return max(0.0, self.duration - self._elapsed)
