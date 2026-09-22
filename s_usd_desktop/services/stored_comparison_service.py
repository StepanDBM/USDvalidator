from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from uuid import UUID

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

from s_usd_desktop.cache import (
    CacheEntryStatus,
    CacheLocation,
    DownloadCancellationToken,
    DownloadCancelledError,
    VerifiedDownloader
)
from s_usd_desktop.client import FileClient, SUsdvApiClient
from s_usd_desktop.services.version_open_service import VersionOpenService
from s_usd_desktop.services.workers import RequestWorker


class ComparisonPairReadiness(str, Enum):
    CHECKING = "checking"
    PREPARATION_REQUIRED = "preparation_required"
    READY = "ready"
    INVALID = "invalid"


@dataclass(frozen=True, slots=True)
class StoredVersionComparisonSource:
    project_code: str
    asset_code: str
    stream_name: str
    version_id: UUID
    version_number: int
    root_file_id: UUID | None
    root_path: Path | None
    readiness: str
    missing_count: int
    invalid_count: int

    @property
    def display_name(self):
        return f"{self.project_code} / {self.asset_code} / {self.stream_name} / v{self.version_number:04d}"

    @property
    def location(self):
        return CacheLocation(
            self.project_code,
            self.asset_code,
            self.stream_name,
            self.version_number
        )


@dataclass(frozen=True, slots=True)
class StoredVersionComparisonPair:
    base: StoredVersionComparisonSource
    target: StoredVersionComparisonSource
    readiness: ComparisonPairReadiness
    message: str

    @property
    def ready(self):
        return self.readiness == ComparisonPairReadiness.READY


class PairPreparationSignals(QObject):
    progress = Signal(int, int, str)
    completed = Signal(object)
    failed = Signal(str)
    cancelled = Signal()
    finished = Signal()


class PairPreparationWorker(QRunnable):
    def __init__(self, configuration, cache_manager, pair, token):
        super().__init__()
        self.configuration = configuration
        self.cache_manager = cache_manager
        self.pair = pair
        self.token = token
        self.signals = PairPreparationSignals()

    @Slot()
    def run(self):
        try:
            with SUsdvApiClient(self.configuration) as api:
                client = FileClient(api)
                sources = (self.pair.base, self.pair.target)
                source_files = [
                    (source, tuple(client.list_files(source.version_id).items))
                    for source in sources
                ]
                pending = []
                for source, files in source_files:
                    for item in files:
                        entry = self.cache_manager.inspect(
                            source.project_code,
                            source.asset_code,
                            source.stream_name,
                            source.version_number,
                            item
                        )
                        if entry.status != CacheEntryStatus.AVAILABLE:
                            pending.append((source, item))

                total = sum(item.size_bytes for _source, item in pending)
                transferred = 0
                downloader = VerifiedDownloader(client, self.cache_manager)

                for source, item in pending:
                    base = transferred
                    downloader.download(
                        item,
                        source.location,
                        token=self.token,
                        progress=lambda sent, _size, offset=base, name=item.relative_path, version=source.version_number: (
                            self.signals.progress.emit(
                                offset + sent,
                                total,
                                f"v{version:04d} / {name}"
                            )
                        )
                    )
                    transferred += item.size_bytes

                prepared = _build_pair(
                    self.cache_manager,
                    source_files[0][0],
                    source_files[0][1],
                    source_files[1][0],
                    source_files[1][1]
                )
                if not prepared.ready:
                    raise RuntimeError(prepared.message)
        except DownloadCancelledError:
            self.signals.cancelled.emit()
        except Exception as error:
            self.signals.failed.emit(getattr(error, "message", str(error)))
        else:
            self.signals.completed.emit(prepared)
        finally:
            self.signals.finished.emit()


class StoredComparisonService(QObject):
    pair_loaded = Signal(object)
    pair_prepared = Signal(object)
    preparation_progress = Signal(int, int, str)
    preparation_failed = Signal(str)
    preparation_cancelled = Signal()
    loading_changed = Signal(bool)
    preparing_changed = Signal(bool)
    request_failed = Signal(str)

    def __init__(self, connection_service, cache_manager, thread_pool=None, parent=None):
        super().__init__(parent)
        self.connection_service = connection_service
        self.cache_manager = cache_manager
        self.thread_pool = thread_pool or QThreadPool.globalInstance()
        self.generation = 0
        self.workers = set()
        self.preparation_worker = None
        self.preparation_token = None

    @property
    def preparing(self):
        return self.preparation_worker is not None

    def resolve_pair(self, project_code, asset_code, stream_name, versions):
        versions = tuple(sorted(versions, key=lambda item: item.number))
        if len(versions) != 2:
            raise ValueError("Exactly two versions are required")
        self.generation += 1
        generation = self.generation
        worker = RequestWorker(
            self._resolve,
            self.connection_service.preferences.to_api_configuration(),
            project_code,
            asset_code,
            stream_name,
            versions
        )
        worker.signals.result.connect(
            lambda pair, current=generation: self._result(current, pair)
        )
        worker.signals.error.connect(
            lambda error, current=generation: self._error(current, error)
        )
        worker.signals.finished.connect(lambda current=worker: self.workers.discard(current))
        self.workers.add(worker)
        self.loading_changed.emit(True)
        self.thread_pool.start(worker)

    def prepare_pair(self, pair):
        if self.preparing:
            raise RuntimeError("Another comparison preparation is already active")
        if pair.readiness == ComparisonPairReadiness.INVALID:
            raise ValueError(pair.message)
        self.preparation_token = DownloadCancellationToken()
        worker = PairPreparationWorker(
            self.connection_service.preferences.to_api_configuration(),
            self.cache_manager,
            pair,
            self.preparation_token
        )
        worker.signals.progress.connect(self.preparation_progress)
        worker.signals.completed.connect(self.pair_prepared)
        worker.signals.failed.connect(self.preparation_failed)
        worker.signals.cancelled.connect(self.preparation_cancelled)
        worker.signals.finished.connect(self._preparation_finished)
        self.preparation_worker = worker
        self.preparing_changed.emit(True)
        self.thread_pool.start(worker)

    def cancel_preparation(self):
        if self.preparation_token:
            self.preparation_token.cancel()

    def invalidate(self):
        self.generation += 1

    def _resolve(self, configuration, project_code, asset_code, stream_name, versions):
        with SUsdvApiClient(configuration) as api:
            client = FileClient(api)
            source_files = []
            for version in versions:
                source = StoredVersionComparisonSource(
                    project_code, asset_code, stream_name, version.id,
                    version.number, None, None, "checking", 0, 0
                )
                source_files.append((source, tuple(client.list_files(version.id).items)))
        return _build_pair(
            self.cache_manager,
            source_files[0][0],
            source_files[0][1],
            source_files[1][0],
            source_files[1][1]
        )

    def _result(self, generation, pair):
        if generation != self.generation:
            return
        self.loading_changed.emit(False)
        self.pair_loaded.emit(pair)

    def _error(self, generation, error):
        if generation != self.generation:
            return
        self.loading_changed.emit(False)
        self.request_failed.emit(getattr(error, "message", str(error)))

    def _preparation_finished(self):
        self.preparation_worker = None
        self.preparation_token = None
        self.preparing_changed.emit(False)


def _build_pair(cache_manager, base_source, base_files, target_source, target_files):
    opener = VersionOpenService(cache_manager)
    sources = []
    for source, files in ((base_source, base_files), (target_source, target_files)):
        resolution = opener.resolve(files, source.location)
        sources.append(StoredVersionComparisonSource(
            project_code=source.project_code,
            asset_code=source.asset_code,
            stream_name=source.stream_name,
            version_id=source.version_id,
            version_number=source.version_number,
            root_file_id=resolution.root_file.id if resolution.root_file else None,
            root_path=resolution.root_path,
            readiness=resolution.readiness.value,
            missing_count=len(resolution.missing_files),
            invalid_count=len(resolution.invalid_files)
        ))
    base, target = sources
    if not base.root_file_id or not target.root_file_id:
        readiness = ComparisonPairReadiness.INVALID
        message = "Both versions must contain exactly one root layer."
    elif all((base.root_path, target.root_path)) and not any((
        base.missing_count, target.missing_count,
        base.invalid_count, target.invalid_count
    )):
        readiness = ComparisonPairReadiness.READY
        message = f"Ready to compare v{base.version_number:04d} with v{target.version_number:04d}."
    else:
        readiness = ComparisonPairReadiness.PREPARATION_REQUIRED
        message = "One or both versions require verified local cache content."
    return StoredVersionComparisonPair(base, target, readiness, message)
