from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Iterable

from s_usd_service.storage.models import StoredObject


class ObjectStorage(ABC):
    @abstractmethod
    def write_stream(
        self,
        source: BinaryIO,
        storage_key: str,
        maximum_bytes: int | None = None
    ) -> StoredObject:
        pass

    @abstractmethod
    def open(self, storage_key: str) -> BinaryIO:
        pass

    @abstractmethod
    def exists(self, storage_key: str) -> bool:
        pass

    @abstractmethod
    def delete(self, storage_key: str) -> bool:
        pass

    @abstractmethod
    def iter_keys(self) -> Iterable[str]:
        pass

    @abstractmethod
    def resolve_local_path(self, storage_key: str) -> Path | None:
        pass
