from datetime import datetime, timezone
from uuid import uuid4

import pytest

from s_usd_desktop.cache import (
    CacheEntry,
    CacheEntryStatus,
    CacheIndex,
    CacheManifestError,
    VersionCacheManifest
)


def make_entry(tmp_path):
    now = datetime.now(timezone.utc)
    return CacheEntry(
        file_id=uuid4(),
        version_id=uuid4(),
        relative_path="root/scene.usda",
        local_path=tmp_path / "files/root/scene.usda",
        size_bytes=12,
        sha256="a" * 64,
        downloaded_at=now,
        last_accessed_at=now,
        status=CacheEntryStatus.AVAILABLE
    )


def test_writes_and_reads_atomic_manifest(tmp_path):
    entry = make_entry(tmp_path)
    path = tmp_path / "cache.json"
    index = CacheIndex()
    index.write(path, VersionCacheManifest(entry.version_id, (entry,)))
    loaded = index.read(path, lambda relative: tmp_path / "files" / relative)

    assert loaded.version_id == entry.version_id
    assert loaded.files[0].file_id == entry.file_id
    assert loaded.files[0].relative_path == "root/scene.usda"
    assert not list(tmp_path.glob("*.tmp"))


def test_rejects_unknown_manifest_schema(tmp_path):
    path = tmp_path / "cache.json"
    path.write_text('{"schema_version": 99, "version_id": "00000000-0000-0000-0000-000000000000"}')

    with pytest.raises(CacheManifestError):
        CacheIndex().read(path, lambda relative: tmp_path / relative)
