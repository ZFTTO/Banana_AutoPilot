import time
from dataclasses import dataclass


def timestamp_ms() -> float:
    return time.perf_counter()


def timestamp_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


@dataclass
class FpsCounter:
    alpha: float = 0.1
    _last: float | None = None
    _fps: float = 0.0

    def tick(self) -> float:
        now = timestamp_ms()

        if self._last is not None:
            dt = now - self._last

            if dt > 0.0:
                instant = 1.0 / dt
                self._fps = (
                    self.alpha * instant
                    + (1 - self.alpha) * self._fps
                )

        self._last = now
        return self._fps

    @property
    def fps(self) -> float:
        return self._fps

    def reset(self) -> None:
        self._last = None
        self._fps = 0.0
        