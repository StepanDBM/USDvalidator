from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from uuid import UUID


class CacheEntryStatus(str, Enum):
    MISSING = "missing"
    AVAILABLE = "available"
    STALE = "stale"
    CORRUPT = "corrupt"


@dataclass(frozen=True, slots=True)
class CacheEntry:
    file_id: UUID
    version_id: UUID
    relative_path: str
    local_path: Path
    size_bytes: int
    sha256: str
    downloaded_at: datetime
    last_accessed_at: datetime
    status: CacheEntryStatus

    def to_dict(self):
        return {
            "file_id": str(self.file_id),
            "version_id": str(self.version_id),
            "relative_path": self.relative_path,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "downloaded_at": self.downloaded_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            "last_accessed_at": self.last_accessed_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        }

    @classmethod
    def from_dict(cls, data, local_path, status=CacheEntryStatus.AVAILABLE):
        return cls(
            file_id=UUID(data["file_id"]),
            version_id=UUID(data["version_id"]),
            relative_path=data["relative_path"],
            local_path=Path(local_path),
            size_bytes=int(data["size_bytes"]),
            sha256=data["sha256"],
            downloaded_at=_parse_datetime(data["downloaded_at"]),
            last_accessed_at=_parse_datetime(data.get("last_accessed_at", data["downloaded_at"])),
            status=status
        )


def _parse_datetime(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
