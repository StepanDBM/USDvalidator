from uuid import UUID

from s_usd_service.database.repositories.files import StoredFileRepository
from s_usd_service.services.version_lifecycle import VersionLifecycleService


class FileLifecycleService:
    def __init__(self, database, storage):
        self.database = database
        self.storage = storage
        self.files = StoredFileRepository(database)
        self.lifecycle = VersionLifecycleService(database)

    def delete(self, file_id: UUID):
        stored_file = self.files.get(file_id)
        version = stored_file.version
        self.lifecycle.ensure_content_mutable(version)
        storage_key = stored_file.storage_key
        object_existed = self.storage.delete(storage_key)

        try:
            self.lifecycle.mark_after_delete(version, stored_file)
            self.database.delete(stored_file)
            self.database.commit()
        except Exception:
            self.database.rollback()
            raise

        return {
            "file_id": file_id,
            "storage_key": storage_key,
            "object_existed": object_existed,
            "metadata_deleted": True
        }
