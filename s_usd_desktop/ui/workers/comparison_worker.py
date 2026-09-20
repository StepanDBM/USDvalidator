from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from s_usd_core.comparison import SemanticComparisonEngine
from s_usd_core.comparison.progress import CancellationToken, ComparisonCancelled, ProgressUpdate
from s_usd_core.comparison.source_preflight import DiffMode
from s_usd_core.comparison.text_diff import build_source_diff


class ComparisonWorker(QObject):
    progress_changed = Signal(object)
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
        self.token = CancellationToken()
        self._terminal_emitted = False

    def request_cancel(self):
        self.token.cancel()

    @Slot()
    def run(self):
        try:
            self.token.raise_if_cancelled()
            self._emit_progress("semantic", "Comparing semantic stage data...", 0, 1)
            comparison = SemanticComparisonEngine(profile=self.profile).compare(
                self.previous,
                self.current,
            )
            self.token.raise_if_cancelled()
            self._emit_progress("semantic", "Semantic comparison complete.", 1, 1)
            result = build_source_diff(
                self.previous,
                self.current,
                self.diff_mode,
                self.token,
                self.progress_changed.emit,
            )
            self.token.raise_if_cancelled()
            self._emit_progress("prepare", "Preparing virtual diff model...", 1, 1)
            self._emit_terminal(self.completed, comparison, result)
        except ComparisonCancelled:
            self._emit_terminal(self.cancelled)
        except Exception as exc:
            self._emit_terminal(self.failed, str(exc))
        finally:
            self.finished.emit()

    def _emit_progress(self, phase, message, current=None, total=None):
        self.progress_changed.emit(ProgressUpdate(phase, message, current, total))

    def _emit_terminal(self, signal, *args):
        if self._terminal_emitted:
            return
        self._terminal_emitted = True
        signal.emit(*args)
