from PySide6.QtCore import QObject, Signal, Slot

from s_usd_core.batch import CancellationToken, SourceDiscoveryOptions, discover_usd_files
from s_usd_core.reporting import ExportOptions, export_batch
from s_usd_core.validation.batch_validator import BatchValidator


class ValidationWorker(QObject):
    started = Signal(int)
    progress_changed = Signal(int, int)
    file_started = Signal(str)
    completed = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self,
        source_path,
        checker,
        discovery_options,
        worker_count=1,
        export_options=None,
        parent=None,
    ):
        super().__init__(parent)
        self.source_path = source_path
        self.checker = checker
        self.discovery_options = discovery_options
        self.worker_count = worker_count
        self.export_options = export_options
        self.cancellation_token = CancellationToken()

    @Slot()
    def run(self):
        try:
            paths = discover_usd_files(self.source_path, self.discovery_options)
            self.started.emit(len(paths))

            if not paths:
                raise ValueError("No supported USD files matched the discovery options.")

            batch = BatchValidator(
                checker=self.checker,
                worker_count=self.worker_count,
            ).validate(
                paths,
                cancellation_token=self.cancellation_token,
                on_file_started=lambda path: self.file_started.emit(str(path)),
                on_progress=lambda done, total: self.progress_changed.emit(done, total),
            )

            if self.export_options:
                export_batch(batch, self.export_options)

            self.completed.emit(batch)
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()

    @Slot()
    def cancel(self):
        self.cancellation_token.cancel()
