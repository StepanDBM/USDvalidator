import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from s_usd_desktop.cache.entry import CacheEntry
from s_usd_desktop.cache.errors import CacheManifestError


SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class VersionCacheManifest:
    version_id: UUID
    files: tuple[CacheEntry, ...] = ()
    schema_version: int = SCHEMA_VERSION

    def to_dict(self):
        return {
            "schema_version": self.schema_version,
            "version_id": str(self.version_id),
            "files": [entry.to_dict() for entry in self.files]
        }


class CacheIndex:
    def read(self, manifest_path, file_path_resolver):
        path = Path(manifest_path)

        if not path.is_file():
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))

            if data.get("schema_version") != SCHEMA_VERSION:
                raise CacheManifestError(
                    f"Unsupported cache manifest schema: {data.get('schema_version')}"
                )

            version_id = UUID(data["version_id"])
            files = tuple(
                CacheEntry.from_dict(item, file_path_resolver(item["relative_path"]))
                for item in data.get("files", ())
            )
            return VersionCacheManifest(version_id=version_id, files=files)
        except CacheManifestError:
            raise
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise CacheManifestError(f"Could not read cache manifest: {path}") from error

    def write(self, manifest_path, manifest):
        path = Path(manifest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent
        )
        temporary_path = Path(temporary_name)

        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(manifest.to_dict(), stream, indent=2, ensure_ascii=False)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())

            os.replace(temporary_path, path)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise
