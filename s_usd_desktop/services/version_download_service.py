from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

from s_usd_desktop.cache import (
    CacheEntryStatus,
    DownloadCancellationToken,
    DownloadCancelledError,
    VerifiedDownloader
)
from s_usd_desktop.client import FileClient, SUsdvApiClient


class VersionDownloadSignals(QObject):
    progress = Signal(int, int, str)
    completed = Signal(object)
    failed = Signal(str)
    cancelled = Signal()
    finished = Signal()


class VersionDownloadWorker(QRunnable):
    def __init__(self, configuration, cache_manager, files, location, token):
        super().__init__()
        self.configuration = configuration
        self.cache_manager = cache_manager
        self.files = tuple(files)
        self.location = location
        self.token = token
        self.signals = VersionDownloadSignals()

    @Slot()
    def run(self):
        completed = []
        pending = []

        for item in self.files:
            entry = self.cache_manager.inspect(
                self.location.project_code,
                self.location.asset_code,
                self.location.stream_name,
                self.location.version_number,
                item
            )
            if entry.status == CacheEntryStatus.AVAILABLE:
                completed.append(entry)
            else:
                pending.append(item)

        total_bytes = sum(item.size_bytes for item in pending)
        base_bytes = 0

        try:
            with SUsdvApiClient(self.configuration) as api:
                downloader = VerifiedDownloader(FileClient(api), self.cache_manager)

                for item in pending:
                    entry = downloader.download(
                        item,
                        self.location,
                        token=self.token,
                        progress=lambda sent, _total, base=base_bytes, name=item.relative_path: (
                            self.signals.progress.emit(base + sent, total_bytes, name)
                        )
                    )
                    completed.append(entry)
                    base_bytes += item.size_bytes
        except DownloadCancelledError:
            self.signals.cancelled.emit()
        except Exception as error:
            self.signals.failed.emit(getattr(error, "message", str(error)))
        else:
            self.signals.completed.emit(tuple(completed))
        finally:
            self.signals.finished.emit()


class VersionDownloadService(QObject):
    progress = Signal(int, int, str)
    completed = Signal(object)
    failed = Signal(str)
    cancelled = Signal()
    active_changed = Signal(bool)

    def __init__(self, connection_service, cache_manager, parent=None):
        super().__init__(parent)
        self.connection_service = connection_service
        self.cache_manager = cache_manager
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(1)
        self.worker = None
        self.token = None

    @property
    def active(self):
        return self.worker is not None

    def download(self, files, location, root_only=False):
        if self.active:
            raise RuntimeError("Another version download is already active")

        files = tuple(files)

        if root_only:
            files = tuple(item for item in files if item.role == "root_layer")

        if not files:
            raise ValueError("No files are available for download")

        self.token = DownloadCancellationToken()
        self.worker = VersionDownloadWorker(
            self.connection_service.preferences.to_api_configuration(),
            self.cache_manager,
            files,
            location,
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
