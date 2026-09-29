from collections.abc import Callable

from s_usd_service.config import ServiceSettings
from s_usd_service.storage.base import ObjectStorage
from s_usd_service.storage.errors import StorageConfigurationError
from s_usd_service.storage.local import LocalObjectStorage

StorageProviderFactory = Callable[[ServiceSettings], ObjectStorage]
_PROVIDER_FACTORIES: dict[str, StorageProviderFactory] = {}


def register_storage_provider(name: str, factory: StorageProviderFactory, *, replace: bool = False) -> None:
    normalized = name.strip().casefold()
    if not normalized:
        raise ValueError("Storage provider name cannot be empty")
    if normalized in _PROVIDER_FACTORIES and not replace:
        raise ValueError(f"Storage provider '{normalized}' is already registered")
    _PROVIDER_FACTORIES[normalized] = factory


def available_storage_providers() -> tuple[str, ...]:
    return tuple(sorted(_PROVIDER_FACTORIES))


def create_object_storage(settings: ServiceSettings) -> ObjectStorage:
    provider_name = settings.storage_provider.strip().casefold()
    factory = _PROVIDER_FACTORIES.get(provider_name)
    if factory is None:
        available = ", ".join(available_storage_providers()) or "<none>"
        raise StorageConfigurationError(
            f"Unsupported storage provider '{settings.storage_provider}'. Available providers: {available}"
        )
    return factory(settings)


def _create_local_storage(settings: ServiceSettings) -> ObjectStorage:
    return LocalObjectStorage(
        root=settings.storage_root,
        temporary_root=settings.temporary_root,
        chunk_size=settings.storage_chunk_size,
    )


register_storage_provider("local", _create_local_storage)
