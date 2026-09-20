from io import BytesIO

import pytest

from s_usd_service.storage.errors import InvalidStorageKeyError, StorageObjectNotFoundError
from s_usd_service.storage.local import LocalObjectStorage


def make_storage(tmp_path, chunk_size=4):
    return LocalObjectStorage(tmp_path / "storage", tmp_path / "temp", chunk_size)


def test_streams_to_temporary_file_then_promotes_atomically(tmp_path):
    storage = make_storage(tmp_path)
    result = storage.write_stream(BytesIO(b"S-USDv storage payload"), "projects/ORBIT/asset/v0001/root.usda")

    assert result.size_bytes == 22
    assert result.sha256 == "cee2198d0eee3e7f377c6f7dfbacdfa8302ebc1dc3c7f7a8f04a63805b95547f"
    assert storage.exists(result.storage_key)
    assert list((tmp_path / "temp").glob("*.part")) == []

    with storage.open(result.storage_key) as source:
        assert source.read() == b"S-USDv storage payload"


def test_rejects_storage_key_traversal(tmp_path):
    storage = make_storage(tmp_path)

    with pytest.raises(InvalidStorageKeyError):
        storage.write_stream(BytesIO(b"bad"), "../outside.usda")


def test_delete_returns_whether_object_existed(tmp_path):
    storage = make_storage(tmp_path)
    key = "projects/ORBIT/asset/v0001/root.usda"
    storage.write_stream(BytesIO(b"content"), key)

    assert storage.delete(key) is True
    assert storage.delete(key) is False

    with pytest.raises(StorageObjectNotFoundError):
        storage.open(key)
