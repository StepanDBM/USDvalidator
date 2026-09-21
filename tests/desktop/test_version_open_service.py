from datetime import datetime, timezone

import pytest

pytest.importorskip("PySide6")
from hashlib import sha256
from types import SimpleNamespace
from uuid import uuid4

from s_usd_desktop.cache import CacheConfiguration, CacheEntry, CacheEntryStatus, CacheLocation, CacheManager
from s_usd_desktop.services.version_open_service import (
    RootLayerMissingError,
    VersionOpenError,
    VersionOpenService,
    VersionReadiness
)


def file_record(role, path, payload):
    return SimpleNamespace(
        id=uuid4(),
        version_id=VERSION_ID,
        role=role,
        relative_path=path,
        size_bytes=len(payload),
        sha256=sha256(payload).hexdigest()
    )


VERSION_ID = uuid4()
LOCATION = CacheLocation("ORB", "rover", "model", 1)


def cache_file(manager, record, payload):
    entry = manager.inspect("ORB", "rover", "model", 1, record)
    entry.local_path.parent.mkdir(parents=True, exist_ok=True)
    entry.local_path.write_bytes(payload)
    now = datetime.now(timezone.utc)
    manager.record(
        "ORB", "rover", "model", 1,
        CacheEntry(
            record.id, record.version_id, record.relative_path, entry.local_path,
            record.size_bytes, record.sha256, now, now, CacheEntryStatus.AVAILABLE
        )
    )
    return entry.local_path


def test_requires_exactly_one_root_layer(tmp_path):
    service = VersionOpenService(CacheManager(CacheConfiguration(root=tmp_path)))
    dependency = file_record("dependency", "geo/body.usda", b"body")

    resolution = service.resolve([dependency], LOCATION)

    assert resolution.readiness == VersionReadiness.NO_ROOT_LAYER


def test_reports_root_not_cached(tmp_path):
    service = VersionOpenService(CacheManager(CacheConfiguration(root=tmp_path)))
    root = file_record("root_layer", "root/scene.usda", b"root")

    assert service.resolve([root], LOCATION).readiness == VersionReadiness.ROOT_NOT_CACHED


def test_reports_uncached_dependencies(tmp_path):
    manager = CacheManager(CacheConfiguration(root=tmp_path))
    service = VersionOpenService(manager)
    root = file_record("root_layer", "root/scene.usda", b"root")
    dependency = file_record("dependency", "geo/body.usda", b"body")
    cache_file(manager, root, b"root")

    resolution = service.resolve([root, dependency], LOCATION)

    assert resolution.readiness == VersionReadiness.DEPENDENCIES_NOT_CACHED
    assert resolution.missing_files == (dependency,)


def test_ready_version_returns_local_root_path(tmp_path):
    manager = CacheManager(CacheConfiguration(root=tmp_path))
    service = VersionOpenService(manager)
    root = file_record("root_layer", "root/scene.usda", b"root")
    dependency = file_record("dependency", "geo/body.usda", b"body")
    root_path = cache_file(manager, root, b"root")
    cache_file(manager, dependency, b"body")

    resolution = service.resolve([root, dependency], LOCATION)

    assert resolution.readiness == VersionReadiness.READY
    assert service.open_path([root, dependency], LOCATION) == root_path
    assert isinstance(root_path, type(tmp_path))
