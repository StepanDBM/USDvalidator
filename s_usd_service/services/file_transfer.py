from pathlib import Path, PurePosixPath
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError

from s_usd_service.database.models import StoredFile
from s_usd_service.database.repositories.catalog import CatalogRepository
from s_usd_service.database.repositories.errors import ConflictError
from s_usd_service.database.repositories.files import StoredFileRepository


class InvalidRelativePathError(ValueError):
    pass


class FileTransferService:
    def __init__(self, database, storage):
        self.database = database
        self.storage = storage
        self.catalog = CatalogRepository(database)
        self.files = StoredFileRepository(database)

    def upload(self, version_id: UUID, source, original_name, relative_path, role, content_type):
        version = self.catalog.get_version(version_id)
        normalized_path = self.normalize_relative_path(relative_path or original_name)
        safe_name = Path(original_name or PurePosixPath(normalized_path).name).name

        if not safe_name:
            raise InvalidRelativePathError("Uploaded file must have a filename")

        if self.files.get_by_relative_path(version_id, normalized_path):
            raise ConflictError(f"A file already exists at '{normalized_path}' in this version")

        storage_key = self._build_storage_key(version, safe_name)
        stored_object = self.storage.write_stream(source, storage_key)
        stored_file = StoredFile(
            version_id=version.id,
            role=role,
            original_name=safe_name,
            relative_path=normalized_path,
            storage_key=stored_object.storage_key,
            content_type=content_type or "application/octet-stream",
            size_bytes=stored_object.size_bytes,
            sha256=stored_object.sha256,
            status="available"
        )

        try:
            self.database.add(stored_file)
            version.status = "uploaded"
            self.database.commit()
            self.database.refresh(stored_file)
            return stored_file
        except IntegrityError as error:
            self.database.rollback()
            self.storage.delete(stored_object.storage_key)
            raise ConflictError("Stored-file metadata conflicts with an existing record") from error
        except Exception:
            self.database.rollback()
            self.storage.delete(stored_object.storage_key)
            raise

    def list_for_version(self, version_id: UUID):
        self.catalog.get_version(version_id)
        return self.files.list_for_version(version_id)

    def get(self, file_id: UUID):
        return self.files.get(file_id)

    @staticmethod
    def normalize_relative_path(relative_path):
        value = (relative_path or "").strip().replace("\\", "/")
        path = PurePosixPath(value)

        if not value or path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
            raise InvalidRelativePathError(f"Invalid relative path: {relative_path}")

        return path.as_posix()

    @staticmethod
    def _build_storage_key(version, safe_name):
        stream = version.stream
        asset = stream.asset
        project = asset.project
        extension = Path(safe_name).suffix.lower()
        object_name = f"{uuid4().hex}{extension}"
        return (
            f"projects/{project.code}/assets/{asset.code}/streams/{stream.name}/"
            f"versions/v{version.number:04d}/objects/{object_name}"
        )
