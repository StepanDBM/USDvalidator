import hashlib
import os
from pathlib import Path, PurePosixPath
from typing import BinaryIO
from uuid import uuid4

from s_usd_service.storage.base import ObjectStorage
from s_usd_service.storage.errors import (
    InvalidStorageKeyError,
    StorageLimitExceededError,
    StorageObjectNotFoundError
)
from s_usd_service.storage.models import StoredObject


class LocalObjectStorage(ObjectStorage):
    def __init__(self, root: Path, temporary_root: Path, chunk_size: int = 1024 * 1024):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        self.root = root.resolve()
        self.temporary_root = temporary_root.resolve()
        self.chunk_size = chunk_size
        self.root.mkdir(parents=True, exist_ok=True)
        self.temporary_root.mkdir(parents=True, exist_ok=True)

    def write_stream(
        self,
        source: BinaryIO,
        storage_key: str,
        maximum_bytes: int | None = None
    ) -> StoredObject:
        normalized_key = self._normalize_key(storage_key)
        destination = self._resolve(normalized_key)
        temporary_path = self.temporary_root / f"{uuid4().hex}.part"
        digest = hashlib.sha256()
        size_bytes = 0

        try:
            with temporary_path.open("xb") as output:
                while chunk := source.read(self.chunk_size):
                    size_bytes += len(chunk)

                    if maximum_bytes is not None and size_bytes > maximum_bytes:
                        raise StorageLimitExceededError(maximum_bytes)

                    output.write(chunk)
                    digest.update(chunk)

                output.flush()
                os.fsync(output.fileno())

            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(temporary_path, destination)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise

        return StoredObject(
            storage_key=normalized_key,
            size_bytes=size_bytes,
            sha256=digest.hexdigest()
        )

    def open(self, storage_key: str) -> BinaryIO:
        path = self._resolve(storage_key)
        if not path.is_file():
            raise StorageObjectNotFoundError(f"Stored object not found: {storage_key}")
        return path.open("rb")

    def exists(self, storage_key: str) -> bool:
        return self._resolve(storage_key).is_file()

    def delete(self, storage_key: str) -> bool:
        path = self._resolve(storage_key)
        if not path.exists():
            return False
        path.unlink()
        self._remove_empty_parents(path.parent)
        return True

    def iter_keys(self):
        if not self.root.exists():
            return iter(())

        return (
            path.relative_to(self.root).as_posix()
            for path in self.root.rglob("*")
            if path.is_file()
        )

    def resolve_local_path(self, storage_key: str) -> Path:
        return self._resolve(storage_key)

    def _resolve(self, storage_key: str) -> Path:
        normalized_key = self._normalize_key(storage_key)
        path = (self.root / Path(*PurePosixPath(normalized_key).parts)).resolve()

        if not path.is_relative_to(self.root):
            raise InvalidStorageKeyError(f"Storage key escapes root: {storage_key}")

        return path

    @staticmethod
    def _normalize_key(storage_key: str) -> str:
        key = storage_key.strip().replace("\\", "/")
        path = PurePosixPath(key)

        if not key or path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
            raise InvalidStorageKeyError(f"Invalid storage key: {storage_key}")

        return path.as_posix()

    def _remove_empty_parents(self, directory: Path):
        while directory != self.root:
            try:
                directory.rmdir()
            except OSError:
                return
            directory = directory.parent
