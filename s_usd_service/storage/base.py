from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO

from s_usd_service.storage.models import StoredObject


class ObjectStorage(ABC):
    @abstractmethod
    def write_stream(self, source: BinaryIO, storage_key: str) -> StoredObject:
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
    def resolve_local_path(self, storage_key: str) -> Path | None:
        pass
