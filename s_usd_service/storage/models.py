from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StoredObject:
    storage_key: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True, slots=True)
class StorageObjectMetadata:
    storage_key: str
    size_bytes: int


@dataclass(frozen=True, slots=True)
class StorageHealth:
    provider: str
    available: bool
    detail: str = ""
