from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from s_usd_desktop.cache import CacheEntryStatus


class VersionReadiness(str, Enum):
    NO_ROOT_LAYER = "no_root_layer"
    ROOT_NOT_CACHED = "root_not_cached"
    DEPENDENCIES_NOT_CACHED = "dependencies_not_cached"
    CACHE_INVALID = "cache_invalid"
    READY = "ready"


class VersionOpenError(Exception):
    pass


class RootLayerMissingError(VersionOpenError):
    pass


@dataclass(frozen=True, slots=True)
class VersionResolution:
    readiness: VersionReadiness
    root_path: Path | None
    root_file: object | None
    missing_files: tuple[object, ...]
    invalid_files: tuple[object, ...]
    cached_files: int
    total_files: int

    @property
    def ready(self):
        return self.readiness == VersionReadiness.READY


class VersionOpenService:
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager

    def resolve(self, files, location):
        files = tuple(files)
        roots = tuple(item for item in files if item.role == "root_layer")

        if len(roots) != 1:
            return VersionResolution(
                VersionReadiness.NO_ROOT_LAYER,
                None,
                roots[0] if roots else None,
                files,
                (),
                0,
                len(files)
            )

        entries = {
            item.id: self.cache_manager.inspect(
                location.project_code,
                location.asset_code,
                location.stream_name,
                location.version_number,
                item
            )
            for item in files
        }
        missing = tuple(item for item in files if entries[item.id].status == CacheEntryStatus.MISSING)
        invalid = tuple(
            item for item in files
            if entries[item.id].status in {CacheEntryStatus.STALE, CacheEntryStatus.CORRUPT}
        )
        cached = len(files) - len(missing) - len(invalid)
        root = roots[0]
        root_entry = entries[root.id]

        if root_entry.status == CacheEntryStatus.MISSING:
            readiness = VersionReadiness.ROOT_NOT_CACHED
        elif root_entry.status in {CacheEntryStatus.STALE, CacheEntryStatus.CORRUPT}:
            readiness = VersionReadiness.CACHE_INVALID
        elif invalid:
            readiness = VersionReadiness.CACHE_INVALID
        elif missing:
            readiness = VersionReadiness.DEPENDENCIES_NOT_CACHED
        else:
            readiness = VersionReadiness.READY

        return VersionResolution(
            readiness,
            root_entry.local_path if root_entry.status == CacheEntryStatus.AVAILABLE else None,
            root,
            missing,
            invalid,
            cached,
            len(files)
        )

    def open_path(self, files, location):
        resolution = self.resolve(files, location)

        if resolution.readiness == VersionReadiness.NO_ROOT_LAYER:
            raise RootLayerMissingError("The version must contain exactly one root_layer file")

        if not resolution.ready:
            raise VersionOpenError(
                f"The version is not ready: {resolution.readiness.value}"
            )

        return resolution.root_path
