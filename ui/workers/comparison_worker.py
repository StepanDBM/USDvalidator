from pathlib import Path
from threading import Event

from PySide6.QtCore import QObject, Signal, Slot

from comparison import SemanticComparisonEngine
from comparison.source_preflight import DiffMode
from comparison.text_diff import DiffCancelled, build_source_diff


class ComparisonWorker(QObject):
    phase_changed = Signal(str)
    completed = Signal(object, object)
    cancelled = Signal()
    failed = Signal(str)
    finished = Signal()

    def __init__(self, previous, current, profile=None, diff_mode=DiffMode.FULL, parent=None):
        super().__init__(parent)
        self.previous = Path(previous)
        self.current = Path(current)
        self.profile = profile
        self.diff_mode = diff_mode
        self._cancelled = Event()

    def request_cancel(self):
        self._cancelled.set()

    @Slot()
    def run(self):
        try:
            if self._cancelled.is_set():
                raise DiffCancelled()
            self.phase_changed.emit("Comparing semantic stage data...")
            comparison = SemanticComparisonEngine(profile=self.profile).compare(
                self.previous,
                self.current,
            )
            if self._cancelled.is_set():
                raise DiffCancelled()
            label = self.diff_mode.value.lower()
            self.phase_changed.emit(f"Building {label} source diff...")
            result = build_source_diff(
                self.previous,
                self.current,
                self.diff_mode,
                self._cancelled.is_set,
            )
            if self._cancelled.is_set():
                raise DiffCancelled()
            self.completed.emit(comparison, result)
        except DiffCancelled:
            self.cancelled.emit()
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()
