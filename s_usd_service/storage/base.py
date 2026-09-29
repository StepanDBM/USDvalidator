from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Iterable

from s_usd_service.storage.models import StorageHealth, StorageObjectMetadata, StoredObject


class ObjectStorage(ABC):
    """Provider-neutral object-storage contract used by service code.

    Providers own key validation, streaming, temporary-write cleanup, atomic
    promotion, and backend-specific health checks. Service layers must not
    assume that stored objects have local filesystem paths.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    def write_stream(self, source: BinaryIO, storage_key: str, maximum_bytes: int | None = None) -> StoredObject:
        pass

    @abstractmethod
    def open(self, storage_key: str) -> BinaryIO:
        pass

    @abstractmethod
    def exists(self, storage_key: str) -> bool:
        pass

    @abstractmethod
    def stat(self, storage_key: str) -> StorageObjectMetadata:
        pass

    @abstractmethod
    def delete(self, storage_key: str) -> bool:
        pass

    @abstractmethod
    def iter_keys(self) -> Iterable[str]:
        pass

    @abstractmethod
    def health(self) -> StorageHealth:
        pass

    def resolve_local_path(self, storage_key: str) -> Path | None:
        """Return a local path only when the provider exposes one.

        Cloud providers intentionally inherit this default. Callers must use
        ``open()`` for provider-independent reads.
        """
        return None
