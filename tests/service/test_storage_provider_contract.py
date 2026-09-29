from io import BytesIO

import pytest

from s_usd_service.storage import LocalObjectStorage
from s_usd_service.storage.errors import InvalidStorageKeyError, StorageLimitExceededError, StorageObjectNotFoundError


@pytest.fixture(params=["local"], ids=lambda provider: provider)
def storage_provider(request, tmp_path):
    if request.param == "local":
        return LocalObjectStorage(tmp_path / "objects", tmp_path / "temporary", chunk_size=3)
    raise AssertionError(f"Unknown contract-test provider: {request.param}")


def test_provider_contract_write_read_stat_iterate_and_delete(storage_provider):
    result = storage_provider.write_stream(BytesIO(b"provider contract"), "workspace/file.usda")

    assert result.storage_key == "workspace/file.usda"
    assert result.size_bytes == 17
    assert len(result.sha256) == 64
    assert storage_provider.exists(result.storage_key)
    assert storage_provider.stat(result.storage_key).size_bytes == 17
    assert set(storage_provider.iter_keys()) == {result.storage_key}

    with storage_provider.open(result.storage_key) as source:
        assert source.read() == b"provider contract"

    assert storage_provider.delete(result.storage_key)
    assert not storage_provider.delete(result.storage_key)
    assert not storage_provider.exists(result.storage_key)


def test_provider_contract_rejects_unsafe_keys(storage_provider):
    for key in ("", "../outside.usda", "/absolute.usda", "root/../../outside.usda"):
        with pytest.raises(InvalidStorageKeyError):
            storage_provider.write_stream(BytesIO(b"unsafe"), key)


def test_provider_contract_enforces_limits_and_cleans_partial_writes(storage_provider):
    with pytest.raises(StorageLimitExceededError):
        storage_provider.write_stream(BytesIO(b"too large"), "limited/file.usda", maximum_bytes=3)

    assert not storage_provider.exists("limited/file.usda")


def test_provider_contract_missing_object_behavior(storage_provider):
    with pytest.raises(StorageObjectNotFoundError):
        storage_provider.open("missing.usda")
    with pytest.raises(StorageObjectNotFoundError):
        storage_provider.stat("missing.usda")


def test_provider_contract_health(storage_provider):
    health = storage_provider.health()
    assert health.provider == storage_provider.provider_name
    assert health.available
