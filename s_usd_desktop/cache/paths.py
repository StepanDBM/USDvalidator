import re
from pathlib import Path, PurePosixPath

from s_usd_desktop.cache.errors import InvalidCachePathError


_SAFE_COMPONENT = re.compile(r"[^A-Za-z0-9._-]+")


def safe_component(value, label="path component"):
    value = str(value).strip()

    if not value or value in {".", ".."} or "/" in value or "\\" in value:
        raise InvalidCachePathError(f"Invalid {label}: {value!r}")

    normalized = _SAFE_COMPONENT.sub("_", value).strip("._")

    if not normalized:
        raise InvalidCachePathError(f"Invalid {label}: {value!r}")

    return normalized


def normalize_relative_path(value):
    raw = str(value).strip().replace("\\", "/")
    path = PurePosixPath(raw)

    if not raw or path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise InvalidCachePathError(f"Invalid relative cache path: {value!r}")

    return path.as_posix()


class CachePaths:
    def __init__(self, root):
        self.root = Path(root).expanduser().resolve()

    def version_root(self, project_code, asset_code, stream_name, version_number):
        version = int(version_number)

        if version < 1:
            raise InvalidCachePathError("Version number must be greater than zero")

        return self._inside_root(
            self.root
            / "projects"
            / safe_component(project_code, "project code")
            / "assets"
            / safe_component(asset_code, "asset code")
            / "streams"
            / safe_component(stream_name, "stream name")
            / f"v{version:04d}"
        )

    def file_path(self, project_code, asset_code, stream_name, version_number, relative_path):
        relative = normalize_relative_path(relative_path)
        parts = PurePosixPath(relative).parts
        path = self.version_root(project_code, asset_code, stream_name, version_number) / "files" / Path(*parts)
        return self._inside_root(path)

    def manifest_path(self, project_code, asset_code, stream_name, version_number):
        return self.version_root(project_code, asset_code, stream_name, version_number) / "cache.json"

    def _inside_root(self, path):
        resolved = Path(path).resolve()

        if not resolved.is_relative_to(self.root):
            raise InvalidCachePathError(f"Cache path escapes root: {path}")

        return resolved
