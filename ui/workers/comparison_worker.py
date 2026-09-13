from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from comparison import SemanticComparisonEngine, build_side_by_side_diff
from comparison.source_preflight import DiffMode


class ComparisonWorker(QObject):
    phase_changed = Signal(str)
    completed = Signal(object, object, object)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, previous, current, profile=None, diff_mode=DiffMode.FULL, parent=None):
        super().__init__(parent)
        self.previous = Path(previous)
        self.current = Path(current)
        self.profile = profile
        self.diff_mode = diff_mode

    @Slot()
    def run(self):
        try:
            self.phase_changed.emit("Building and comparing semantic stage data...")
            comparison = SemanticComparisonEngine(profile=self.profile).compare(
                self.previous,
                self.current,
            )

            if self.diff_mode is DiffMode.SKIP:
                self.phase_changed.emit("Source diff skipped. Finalizing comparison...")
                diff_rows = ()
            else:
                label = "summary" if self.diff_mode is DiffMode.SUMMARY else "full"
                self.phase_changed.emit(f"Building {label} side-by-side source diff...")
                diff_rows = build_side_by_side_diff(
                    self.previous,
                    self.current,
                    mode=self.diff_mode,
                )

            self.completed.emit(comparison, diff_rows, self.diff_mode)
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()
