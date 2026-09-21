from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from s_usd_service.database.models import StoredFile
from s_usd_service.database.repositories.errors import NotFoundError


class StoredFileRepository:
    def __init__(self, database: Session):
        self.database = database

    def get(self, file_id: UUID):
        stored_file = self.database.get(StoredFile, file_id)
        if not stored_file:
            raise NotFoundError("Stored file not found")
        return stored_file

    def get_by_relative_path(self, version_id: UUID, relative_path: str):
        statement = select(StoredFile).where(
            StoredFile.version_id == version_id,
            StoredFile.relative_path == relative_path
        )
        return self.database.scalar(statement)

    def get_by_role(self, version_id: UUID, role: str):
        statement = select(StoredFile).where(
            StoredFile.version_id == version_id,
            StoredFile.role == role
        )
        return self.database.scalar(statement)

    def list_for_version(self, version_id: UUID):
        statement = (
            select(StoredFile)
            .where(StoredFile.version_id == version_id)
            .order_by(StoredFile.relative_path)
        )
        return list(self.database.scalars(statement).all())

    def list_all(self):
        return list(self.database.scalars(select(StoredFile).order_by(StoredFile.storage_key)).all())

    def delete(self, stored_file):
        self.database.delete(stored_file)
        self.database.commit()

    def commit(self):
        self.database.commit()
