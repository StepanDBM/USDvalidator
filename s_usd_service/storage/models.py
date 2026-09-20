from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StoredObject:
    storage_key: str
    size_bytes: int
    sha256: str
