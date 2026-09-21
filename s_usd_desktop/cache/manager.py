import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from s_usd_desktop.cache.configuration import CacheConfiguration
from s_usd_desktop.cache.entry import CacheEntry, CacheEntryStatus
from s_usd_desktop.cache.index import CacheIndex, VersionCacheManifest
from s_usd_desktop.cache.paths import CachePaths, normalize_relative_path


class CacheManager:
    def __init__(self, configuration=None):
        self.configuration = configuration or CacheConfiguration()
        self.paths = CachePaths(self.configuration.root)
        self.index = CacheIndex()

    def inspect(
        self,
        project_code,
        asset_code,
        stream_name,
        version_number,
        stored_file
    ):
        local_path = self.paths.file_path(
            project_code,
            asset_code,
            stream_name,
            version_number,
            stored_file.relative_path
        )
        manifest = self.read_manifest(
            project_code,
            asset_code,
            stream_name,
            version_number
        )
        manifest_entry = self._find_entry(manifest, stored_file.id)
        status = self._status(local_path, stored_file, manifest_entry)
        now = datetime.now(timezone.utc)
        return CacheEntry(
            file_id=UUID(str(stored_file.id)),
            version_id=UUID(str(stored_file.version_id)),
            relative_path=normalize_relative_path(stored_file.relative_path),
            local_path=local_path,
            size_bytes=int(stored_file.size_bytes),
            sha256=stored_file.sha256,
            downloaded_at=manifest_entry.downloaded_at if manifest_entry else now,
            last_accessed_at=manifest_entry.last_accessed_at if manifest_entry else now,
            status=status
        )

    def read_manifest(self, project_code, asset_code, stream_name, version_number):
        manifest_path = self.paths.manifest_path(
            project_code,
            asset_code,
            stream_name,
            version_number
        )
        return self.index.read(
            manifest_path,
            lambda relative_path: self.paths.file_path(
                project_code,
                asset_code,
                stream_name,
                version_number,
                relative_path
            )
        )

    def record(self, project_code, asset_code, stream_name, version_number, entry):
        manifest_path = self.paths.manifest_path(
            project_code,
            asset_code,
            stream_name,
            version_number
        )
        existing = self.read_manifest(project_code, asset_code, stream_name, version_number)
        entries = {item.file_id: item for item in existing.files} if existing else {}
        entries[entry.file_id] = entry
        manifest = VersionCacheManifest(
            version_id=entry.version_id,
            files=tuple(sorted(entries.values(), key=lambda item: item.relative_path.lower()))
        )
        self.index.write(manifest_path, manifest)
        return manifest

    def remove_file(self, project_code, asset_code, stream_name, version_number, file_id):
        manifest = self.read_manifest(project_code, asset_code, stream_name, version_number)

        if not manifest:
            return False

        file_id = UUID(str(file_id))
        entry = self._find_entry(manifest, file_id)

        if not entry:
            return False

        existed = entry.local_path.exists()
        entry.local_path.unlink(missing_ok=True)
        remaining = tuple(item for item in manifest.files if item.file_id != file_id)
        manifest_path = self.paths.manifest_path(
            project_code,
            asset_code,
            stream_name,
            version_number
        )

        if remaining:
            self.index.write(
                manifest_path,
                VersionCacheManifest(version_id=manifest.version_id, files=remaining)
            )
        else:
            manifest_path.unlink(missing_ok=True)
            self._remove_empty_parents(manifest_path.parent)

        return existed

    def clear_version(self, project_code, asset_code, stream_name, version_number):
        version_root = self.paths.version_root(
            project_code,
            asset_code,
            stream_name,
            version_number
        )

        if not version_root.exists():
            return False

        shutil.rmtree(version_root)
        self._remove_empty_parents(version_root.parent)
        return True

    def _status(self, local_path, stored_file, manifest_entry):
        if not local_path.is_file():
            return CacheEntryStatus.MISSING

        if (
            not manifest_entry
            or manifest_entry.file_id != UUID(str(stored_file.id))
            or manifest_entry.version_id != UUID(str(stored_file.version_id))
            or manifest_entry.relative_path != normalize_relative_path(stored_file.relative_path)
            or manifest_entry.size_bytes != int(stored_file.size_bytes)
            or manifest_entry.sha256.lower() != stored_file.sha256.lower()
        ):
            return CacheEntryStatus.STALE

        if local_path.stat().st_size != int(stored_file.size_bytes):
            return CacheEntryStatus.CORRUPT

        if self.configuration.verify_on_access and self._sha256(local_path) != stored_file.sha256.lower():
            return CacheEntryStatus.CORRUPT

        return CacheEntryStatus.AVAILABLE

    @staticmethod
    def _find_entry(manifest, file_id):
        if not manifest:
            return None

        target = UUID(str(file_id))
        return next((item for item in manifest.files if item.file_id == target), None)

    @staticmethod
    def _sha256(path):
        digest = hashlib.sha256()

        with Path(path).open("rb") as source:
            while chunk := source.read(1024 * 1024):
                digest.update(chunk)

        return digest.hexdigest()

    def _remove_empty_parents(self, directory):
        directory = Path(directory)

        while directory != self.configuration.root:
            try:
                directory.rmdir()
            except OSError:
                return
            directory = directory.parent
