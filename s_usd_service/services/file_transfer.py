from pathlib import Path, PurePosixPath
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError

from s_usd_service.config import get_settings
from s_usd_service.database.models import StoredFile
from s_usd_service.database.repositories.catalog import CatalogRepository
from s_usd_service.database.repositories.errors import ConflictError
from s_usd_service.database.repositories.files import StoredFileRepository
from s_usd_service.services.version_lifecycle import VersionLifecycleService


class InvalidUploadError(ValueError):
    pass


class InvalidRelativePathError(InvalidUploadError):
    pass


class EmptyUploadError(InvalidUploadError):
    pass


class UnsupportedFileExtensionError(InvalidUploadError):
    pass


class InvalidFileRoleError(InvalidUploadError):
    pass


class FileTransferService:
    def __init__(self, database, storage, settings=None):
        self.database = database
        self.storage = storage
        self.settings = settings or get_settings()
        self.catalog = CatalogRepository(database)
        self.files = StoredFileRepository(database)

    def upload(self, version_id: UUID, source, original_name, relative_path, role, content_type):
        version = self.catalog.get_version(version_id)
        lifecycle = VersionLifecycleService(self.database)
        lifecycle.ensure_content_mutable(version)
        normalized_path = self.normalize_relative_path(relative_path or original_name)
        safe_name = Path(original_name or PurePosixPath(normalized_path).name).name
        normalized_role = role.strip().lower()
        self._validate_upload(version_id, safe_name, normalized_path, normalized_role)
        storage_key = self._build_storage_key(version, safe_name)
        stored_object = self.storage.write_stream(
            source,
            storage_key,
            maximum_bytes=self.settings.maximum_upload_bytes
        )

        if stored_object.size_bytes == 0:
            self.storage.delete(stored_object.storage_key)
            raise EmptyUploadError("Empty files cannot be uploaded")

        stored_file = StoredFile(
            version_id=version.id,
            role=normalized_role,
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
            lifecycle.mark_after_upload(version, stored_file)
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

    def _validate_upload(self, version_id, safe_name, relative_path, role):
        if not safe_name:
            raise InvalidRelativePathError("Uploaded file must have a filename")

        if role not in self.settings.allowed_file_roles:
            allowed = ", ".join(self.settings.allowed_file_roles)
            raise InvalidFileRoleError(f"Unsupported file role '{role}'. Allowed roles: {allowed}")

        extension = Path(safe_name).suffix.lower()
        logical_extension = PurePosixPath(relative_path).suffix.lower()

        if extension not in self.settings.allowed_usd_extensions:
            allowed = ", ".join(self.settings.allowed_usd_extensions)
            raise UnsupportedFileExtensionError(
                f"Unsupported file extension '{extension or '<none>'}'. Allowed extensions: {allowed}"
            )

        if logical_extension != extension:
            raise UnsupportedFileExtensionError(
                "The uploaded filename and relative path must use the same USD extension"
            )

        if self.files.get_by_relative_path(version_id, relative_path):
            raise ConflictError(f"A file already exists at '{relative_path}' in this version")

        if role == "root_layer" and self.files.get_by_role(version_id, "root_layer"):
            raise ConflictError("A version can contain only one root_layer file")

    @staticmethod
    def normalize_relative_path(relative_path):
        value = (relative_path or "").strip().replace("\\", "/")
        path = PurePosixPath(value)

        if not value or path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
            raise InvalidRelativePathError(f"Invalid relative path: {relative_path}")

        if len(value) > 1024:
            raise InvalidRelativePathError("Relative path exceeds 1024 characters")

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
