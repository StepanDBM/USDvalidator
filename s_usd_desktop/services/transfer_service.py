from dataclasses import dataclass
from pathlib import Path
from threading import Event

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

from s_usd_desktop.client import FileClient, SUsdvApiClient


class TransferCancelledError(Exception):
    pass


class CancellationToken:
    def __init__(self):
        self._event = Event()

    @property
    def cancelled(self):
        return self._event.is_set()

    def cancel(self):
        self._event.set()


class ProgressFile:
    def __init__(self, source, total_bytes, callback, token):
        self.source = source
        self.total_bytes = total_bytes
        self.callback = callback
        self.token = token
        self.transferred = 0

    def read(self, size=-1):
        if self.token.cancelled:
            raise TransferCancelledError("Upload cancelled")

        chunk = self.source.read(size)
        self.transferred += len(chunk)
        self.callback(self.transferred, self.total_bytes)
        return chunk

    def __getattr__(self, name):
        return getattr(self.source, name)


class UploadSignals(QObject):
    progress = Signal(int, int)
    completed = Signal(object)
    failed = Signal(str)
    cancelled = Signal()
    finished = Signal()


class UploadWorker(QRunnable):
    def __init__(self, configuration, version_id, source_path, role, relative_path, token):
        super().__init__()
        self.configuration = configuration
        self.version_id = version_id
        self.source_path = Path(source_path)
        self.role = role
        self.relative_path = relative_path
        self.token = token
        self.signals = UploadSignals()

    @Slot()
    def run(self):
        try:
            total_bytes = self.source_path.stat().st_size

            with self.source_path.open("rb") as source:
                progress_source = ProgressFile(
                    source,
                    total_bytes,
                    self.signals.progress.emit,
                    self.token
                )

                with SUsdvApiClient(self.configuration) as api:
                    result = FileClient(api).upload_stream(
                        self.version_id,
                        progress_source,
                        self.source_path.name,
                        self.role,
                        self.relative_path
                    )
        except TransferCancelledError:
            self.signals.cancelled.emit()
        except Exception as error:
            self.signals.failed.emit(getattr(error, "message", str(error)))
        else:
            self.signals.completed.emit(result)
        finally:
            self.signals.finished.emit()


class TransferService(QObject):
    progress = Signal(int, int)
    upload_completed = Signal(object)
    upload_failed = Signal(str)
    upload_cancelled = Signal()
    active_changed = Signal(bool)

    def __init__(self, connection_service, thread_pool=None, parent=None):
        super().__init__(parent)
        self.connection_service = connection_service
        self.thread_pool = thread_pool or QThreadPool()
        self.thread_pool.setMaxThreadCount(1)
        self.worker = None
        self.token = None

    @property
    def active(self):
        return self.worker is not None

    def upload(self, version_id, source_path, role, relative_path):
        if self.active:
            raise RuntimeError("Another transfer is already active")

        self.token = CancellationToken()
        self.worker = UploadWorker(
            self.connection_service.preferences.to_api_configuration(),
            version_id,
            source_path,
            role,
            relative_path,
            self.token
        )
        self.worker.signals.progress.connect(self.progress)
        self.worker.signals.completed.connect(self.upload_completed)
        self.worker.signals.failed.connect(self.upload_failed)
        self.worker.signals.cancelled.connect(self.upload_cancelled)
        self.worker.signals.finished.connect(self._finished)
        self.active_changed.emit(True)
        self.thread_pool.start(self.worker)

    def cancel(self):
        if self.token:
            self.token.cancel()

    def _finished(self):
        self.worker = None
        self.token = None
        self.active_changed.emit(False)
