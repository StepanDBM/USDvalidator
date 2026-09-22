import hashlib
import json
from pathlib import Path
from uuid import uuid4

from s_usd_desktop.cache import ManagedCacheRecognizer


def create_cached_file(root):
    version_id = uuid4()
    file_id = uuid4()
    version_root = root / "projects/EXP/assets/probe/streams/model/versions/v0002"
    local_path = version_root / "files/root/probe.usda"
    local_path.parent.mkdir(parents=True)
    local_path.write_text("#usda 1.0\n", encoding="utf-8")
    (version_root / "cache.json").write_text(json.dumps({
        "schema_version": 1,
        "version_id": str(version_id),
        "files": [{
            "file_id": str(file_id),
            "version_id": str(version_id),
            "relative_path": "root/probe.usda",
            "size_bytes": local_path.stat().st_size,
            "sha256": hashlib.sha256(local_path.read_bytes()).hexdigest(),
            "downloaded_at": "2026-09-22T00:00:00Z",
            "last_accessed_at": "2026-09-22T00:00:00Z"
        }]
    }), encoding="utf-8")
    return local_path, version_id, file_id


def test_recognizes_file_inside_managed_cache(tmp_path):
    local_path, version_id, file_id = create_cached_file(tmp_path)

    source = ManagedCacheRecognizer(tmp_path).recognize(local_path)

    assert source.project_code == "EXP"
    assert source.asset_code == "probe"
    assert source.stream_name == "model"
    assert source.version_number == 2
    assert source.version_id == version_id
    assert source.file_id == file_id
    assert source.relative_path == "root/probe.usda"


def test_ignores_unmanaged_and_unregistered_files(tmp_path):
    unmanaged = tmp_path.parent / "outside.usda"
    unmanaged.write_text("#usda 1.0\n", encoding="utf-8")
    assert ManagedCacheRecognizer(tmp_path).recognize(unmanaged) is None

    registered, _version_id, _file_id = create_cached_file(tmp_path)
    extra = registered.parent / "extra.usda"
    extra.write_text("#usda 1.0\n", encoding="utf-8")
    assert ManagedCacheRecognizer(tmp_path).recognize(extra) is None


def test_rejects_size_mismatch(tmp_path):
    local_path, _version_id, _file_id = create_cached_file(tmp_path)
    local_path.write_text("changed", encoding="utf-8")

    assert ManagedCacheRecognizer(tmp_path).recognize(local_path) is None
