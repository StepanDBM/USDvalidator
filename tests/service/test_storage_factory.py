from pathlib import Path

import pytest

from s_usd_service.config import ServiceSettings
from s_usd_service.storage import LocalObjectStorage, ObjectStorage, create_object_storage, register_storage_provider
from s_usd_service.storage.errors import StorageConfigurationError
from s_usd_service.storage.models import StorageHealth


def settings(tmp_path, provider="local"):
    return ServiceSettings(
        data_root=tmp_path,
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        storage_provider=provider,
        storage_root=tmp_path / "objects",
        temporary_root=tmp_path / "temporary",
    )


def test_factory_builds_configured_local_provider(tmp_path):
    storage = create_object_storage(settings(tmp_path))
    assert isinstance(storage, LocalObjectStorage)
    assert storage.provider_name == "local"
    assert storage.root == (tmp_path / "objects").resolve()


def test_factory_rejects_unknown_provider(tmp_path):
    with pytest.raises(StorageConfigurationError, match="Unsupported storage provider 'azure'"):
        create_object_storage(settings(tmp_path, "azure"))


def test_external_provider_can_register_without_service_changes(tmp_path):
    class ExampleCloudStorage(ObjectStorage):
        provider_name = "example-cloud"

        def write_stream(self, source, storage_key, maximum_bytes=None):
            raise NotImplementedError

        def open(self, storage_key):
            raise NotImplementedError

        def exists(self, storage_key):
            return False

        def stat(self, storage_key):
            raise NotImplementedError

        def delete(self, storage_key):
            return False

        def iter_keys(self):
            return iter(())

        def health(self):
            return StorageHealth(self.provider_name, True)

    register_storage_provider("example-cloud", lambda _settings: ExampleCloudStorage(), replace=True)
    storage = create_object_storage(settings(tmp_path, "example-cloud"))
    assert storage.provider_name == "example-cloud"
    assert storage.resolve_local_path("anything") is None
