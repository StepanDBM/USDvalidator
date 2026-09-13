from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from comparison import SemanticComparisonEngine, build_side_by_side_diff


class ComparisonWorker(QObject):
    phase_changed = Signal(str)
    completed = Signal(object, object)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, previous, current, profile=None, parent=None):
        super().__init__(parent)
        self.previous = Path(previous)
        self.current = Path(current)
        self.profile = profile

    @Slot()
    def run(self):
        try:
            self.phase_changed.emit("Building and comparing semantic stage data...")

            comparison = SemanticComparisonEngine(
                profile=self.profile
            ).compare(
                self.previous,
                self.current,
            )

            self.phase_changed.emit("Building side-by-side source diff...")

            diff_rows = build_side_by_side_diff(
                self.previous,
                self.current,
            )

            self.completed.emit(comparison, diff_rows)

        except Exception as exc:
            self.failed.emit(str(exc))

        finally:
            self.finished.emit()