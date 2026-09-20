from dataclasses import dataclass
from threading import Event


class ComparisonCancelled(Exception):
    pass


class CancellationToken:
    def __init__(self):
        self._event = Event()

    @property
    def cancelled(self):
        return self._event.is_set()

    def cancel(self):
        self._event.set()

    def raise_if_cancelled(self):
        if self.cancelled:
            raise ComparisonCancelled("Comparison cancelled.")


@dataclass(frozen=True)
class ProgressUpdate:
    phase: str
    message: str
    current: int | None = None
    total: int | None = None

    @property
    def determinate(self):
        return self.current is not None and self.total is not None and self.total > 0

    @property
    def percent(self):
        if not self.determinate:
            return None
        return max(0, min(100, round(self.current * 100 / self.total)))
