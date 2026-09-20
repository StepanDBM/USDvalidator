from uuid import UUID

from s_usd_service.database.repositories.files import StoredFileRepository


class FileLifecycleService:
    def __init__(self, database, storage):
        self.database = database
        self.storage = storage
        self.files = StoredFileRepository(database)

    def delete(self, file_id: UUID):
        stored_file = self.files.get(file_id)
        storage_key = stored_file.storage_key
        object_existed = self.storage.delete(storage_key)

        try:
            self.files.delete(stored_file)
        except Exception:
            self.database.rollback()
            raise

        return {
            "file_id": file_id,
            "storage_key": storage_key,
            "object_existed": object_existed,
            "metadata_deleted": True
        }
