import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ManagedCacheSource:
    project_code: str
    asset_code: str
    stream_name: str
    version_number: int
    version_id: UUID
    file_id: UUID
    relative_path: str
    local_path: Path

    @property
    def display_name(self):
        return (
            f"Managed cache: {self.project_code} / {self.asset_code} / "
            f"{self.stream_name} / v{self.version_number:04d} / {self.relative_path}"
        )


class ManagedCacheRecognizer:
    def __init__(self, cache_root):
        self.cache_root = Path(cache_root).expanduser().resolve()

    def recognize(self, source_path):
        path = Path(source_path).expanduser().resolve()

        try:
            relative = path.relative_to(self.cache_root)
        except ValueError:
            return None

        parts = relative.parts
        if len(parts) < 11 or parts[0] != "projects" or parts[2] != "assets":
            return None
        if parts[4] != "streams" or parts[6] != "versions" or parts[8] != "files":
            return None

        version_name = parts[7]
        if not version_name.startswith("v") or not version_name[1:].isdigit():
            return None

        version_root = self.cache_root.joinpath(*parts[:8])
        manifest_path = version_root / "cache.json"
        if not manifest_path.is_file() or not path.is_file():
            return None

        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            relative_path = Path(*parts[9:]).as_posix()
            entry = next(
                item for item in data.get("files", ())
                if item.get("relative_path") == relative_path
            )
            if path.stat().st_size != int(entry["size_bytes"]):
                return None
            if self._sha256(path) != str(entry["sha256"]).lower():
                return None
            return ManagedCacheSource(
                project_code=parts[1],
                asset_code=parts[3],
                stream_name=parts[5],
                version_number=int(version_name[1:]),
                version_id=UUID(data["version_id"]),
                file_id=UUID(entry["file_id"]),
                relative_path=relative_path,
                local_path=path
            )
        except (OSError, ValueError, KeyError, StopIteration, TypeError):
            return None

    @staticmethod
    def _sha256(path):
        digest = hashlib.sha256()
        with path.open("rb") as source:
            while chunk := source.read(1024 * 1024):
                digest.update(chunk)
        return digest.hexdigest()
