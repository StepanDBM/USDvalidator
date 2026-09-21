from dataclasses import dataclass

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

from s_usd_desktop.cache import CacheManager
from s_usd_desktop.cache.downloader import (
    CacheLocation,
    DownloadCancellationToken,
    DownloadCancelledError,
    VerifiedDownloader
)
from s_usd_desktop.client import FileClient, SUsdvApiClient


@dataclass(frozen=True, slots=True)
class DownloadRequest:
    stored_file: object
    location: CacheLocation


class DownloadSignals(QObject):
    progress = Signal(int, int)
    completed = Signal(object)
    failed = Signal(str)
    cancelled = Signal()
    finished = Signal()


class DownloadWorker(QRunnable):
    def __init__(self, configuration, cache_manager, request, token):
        super().__init__()
        self.configuration = configuration
        self.cache_manager = cache_manager
        self.request = request
        self.token = token
        self.signals = DownloadSignals()

    @Slot()
    def run(self):
        try:
            with SUsdvApiClient(self.configuration) as api:
                entry = VerifiedDownloader(FileClient(api), self.cache_manager).download(
                    self.request.stored_file,
                    self.request.location,
                    progress=self.signals.progress.emit,
                    token=self.token
                )
        except DownloadCancelledError:
            self.signals.cancelled.emit()
        except Exception as error:
            self.signals.failed.emit(getattr(error, "message", str(error)))
        else:
            self.signals.completed.emit(entry)
        finally:
            self.signals.finished.emit()


class DownloadService(QObject):
    progress = Signal(int, int)
    completed = Signal(object)
    failed = Signal(str)
    cancelled = Signal()
    active_changed = Signal(bool)

    def __init__(self, connection_service, cache_manager=None, thread_pool=None, parent=None):
        super().__init__(parent)
        self.connection_service = connection_service
        self.cache_manager = cache_manager or CacheManager()
        self.thread_pool = thread_pool or QThreadPool()
        self.thread_pool.setMaxThreadCount(1)
        self.worker = None
        self.token = None

    @property
    def active(self):
        return self.worker is not None

    def download(self, stored_file, location):
        if self.active:
            raise RuntimeError("Another download is already active")

        self.token = DownloadCancellationToken()
        self.worker = DownloadWorker(
            self.connection_service.preferences.to_api_configuration(),
            self.cache_manager,
            DownloadRequest(stored_file, location),
            self.token
        )
        self.worker.signals.progress.connect(self.progress)
        self.worker.signals.completed.connect(self.completed)
        self.worker.signals.failed.connect(self.failed)
        self.worker.signals.cancelled.connect(self.cancelled)
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
