from datetime import datetime, timezone
from hashlib import sha256
from types import SimpleNamespace
from uuid import uuid4

from s_usd_desktop.cache import CacheConfiguration, CacheEntry, CacheEntryStatus, CacheManager


def remote_file(payload=b"#usda 1.0\n"):
    return SimpleNamespace(
        id=uuid4(),
        version_id=uuid4(),
        relative_path="root/scene.usda",
        size_bytes=len(payload),
        sha256=sha256(payload).hexdigest()
    )


def test_inspect_reports_missing_before_download(tmp_path):
    manager = CacheManager(CacheConfiguration(root=tmp_path))
    entry = manager.inspect("ORB", "rover", "model", 1, remote_file())

    assert entry.status == CacheEntryStatus.MISSING
    assert entry.local_path == tmp_path / "projects/ORB/assets/rover/streams/model/v0001/files/root/scene.usda"


def test_inspect_reports_available_after_recording(tmp_path):
    payload = b"#usda 1.0\n"
    remote = remote_file(payload)
    manager = CacheManager(CacheConfiguration(root=tmp_path))
    inspected = manager.inspect("ORB", "rover", "model", 1, remote)
    inspected.local_path.parent.mkdir(parents=True, exist_ok=True)
    inspected.local_path.write_bytes(payload)
    now = datetime.now(timezone.utc)
    manager.record(
        "ORB",
        "rover",
        "model",
        1,
        CacheEntry(
            remote.id,
            remote.version_id,
            remote.relative_path,
            inspected.local_path,
            remote.size_bytes,
            remote.sha256,
            now,
            now,
            CacheEntryStatus.AVAILABLE
        )
    )

    assert manager.inspect("ORB", "rover", "model", 1, remote).status == CacheEntryStatus.AVAILABLE


def test_inspect_detects_size_and_checksum_corruption(tmp_path):
    payload = b"#usda 1.0\n"
    remote = remote_file(payload)
    manager = CacheManager(CacheConfiguration(root=tmp_path))
    inspected = manager.inspect("ORB", "rover", "model", 1, remote)
    inspected.local_path.parent.mkdir(parents=True, exist_ok=True)
    inspected.local_path.write_bytes(payload)
    now = datetime.now(timezone.utc)
    entry = CacheEntry(
        remote.id,
        remote.version_id,
        remote.relative_path,
        inspected.local_path,
        remote.size_bytes,
        remote.sha256,
        now,
        now,
        CacheEntryStatus.AVAILABLE
    )
    manager.record("ORB", "rover", "model", 1, entry)
    inspected.local_path.write_bytes(b"bad")

    assert manager.inspect("ORB", "rover", "model", 1, remote).status == CacheEntryStatus.CORRUPT


def test_metadata_changes_mark_existing_file_stale(tmp_path):
    payload = b"#usda 1.0\n"
    remote = remote_file(payload)
    manager = CacheManager(CacheConfiguration(root=tmp_path))
    inspected = manager.inspect("ORB", "rover", "model", 1, remote)
    inspected.local_path.parent.mkdir(parents=True, exist_ok=True)
    inspected.local_path.write_bytes(payload)
    now = datetime.now(timezone.utc)
    manager.record(
        "ORB", "rover", "model", 1,
        CacheEntry(remote.id, remote.version_id, remote.relative_path, inspected.local_path, len(payload), remote.sha256, now, now, CacheEntryStatus.AVAILABLE)
    )
    remote.sha256 = "0" * 64

    assert manager.inspect("ORB", "rover", "model", 1, remote).status == CacheEntryStatus.STALE


def test_remove_file_and_clear_version(tmp_path):
    payload = b"#usda 1.0\n"
    remote = remote_file(payload)
    manager = CacheManager(CacheConfiguration(root=tmp_path))
    inspected = manager.inspect("ORB", "rover", "model", 1, remote)
    inspected.local_path.parent.mkdir(parents=True, exist_ok=True)
    inspected.local_path.write_bytes(payload)
    now = datetime.now(timezone.utc)
    manager.record(
        "ORB", "rover", "model", 1,
        CacheEntry(remote.id, remote.version_id, remote.relative_path, inspected.local_path, len(payload), remote.sha256, now, now, CacheEntryStatus.AVAILABLE)
    )

    assert manager.remove_file("ORB", "rover", "model", 1, remote.id) is True
    assert inspected.local_path.exists() is False

    version_root = manager.paths.version_root("ORB", "rover", "model", 2)
    version_root.mkdir(parents=True)
    (version_root / "cache.json").write_text("{}")
    assert manager.clear_version("ORB", "rover", "model", 2) is True
    assert version_root.exists() is False
