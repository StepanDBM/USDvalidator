from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from uuid import UUID

from PySide6.QtCore import QObject, QThreadPool, Signal

from s_usd_desktop.cache import CacheLocation
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


@dataclass(frozen=True, slots=True)
class StoredVersionComparisonPair:
    base: StoredVersionComparisonSource
    target: StoredVersionComparisonSource
    readiness: ComparisonPairReadiness
    message: str

    @property
    def ready(self):
        return self.readiness == ComparisonPairReadiness.READY


class StoredComparisonService(QObject):
    pair_loaded = Signal(object)
    loading_changed = Signal(bool)
    request_failed = Signal(str)

    def __init__(self, connection_service, cache_manager, thread_pool=None, parent=None):
        super().__init__(parent)
        self.connection_service = connection_service
        self.cache_manager = cache_manager
        self.thread_pool = thread_pool or QThreadPool.globalInstance()
        self.generation = 0
        self.workers = set()

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

    def invalidate(self):
        self.generation += 1

    def _resolve(self, configuration, project_code, asset_code, stream_name, versions):
        opener = VersionOpenService(self.cache_manager)
        sources = []
        with SUsdvApiClient(configuration) as api:
            client = FileClient(api)
            for version in versions:
                files = client.list_files(version.id).items
                location = CacheLocation(project_code, asset_code, stream_name, version.number)
                resolution = opener.resolve(files, location)
                sources.append(StoredVersionComparisonSource(
                    project_code=project_code,
                    asset_code=asset_code,
                    stream_name=stream_name,
                    version_id=version.id,
                    version_number=version.number,
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
        elif base.root_path and target.root_path and not base.missing_count and not target.missing_count and not base.invalid_count and not target.invalid_count:
            readiness = ComparisonPairReadiness.READY
            message = f"Ready to compare v{base.version_number:04d} with v{target.version_number:04d}."
        else:
            readiness = ComparisonPairReadiness.PREPARATION_REQUIRED
            message = "One or both versions require verified local cache content."
        return StoredVersionComparisonPair(base, target, readiness, message)

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
