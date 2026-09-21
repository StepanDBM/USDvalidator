from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from s_usd_service.database.models import StoredFile, ValidationRun, Version
from s_usd_service.database.repositories.errors import NotFoundError


class ValidationRunRepository:
    def __init__(self, database: Session):
        self.database = database

    def create(self, version_id: UUID, data):
        version = self.database.get(Version, version_id)
        if not version:
            raise NotFoundError("Version not found")

        stored_file_id = data.get("stored_file_id")
        if stored_file_id:
            stored_file = self.database.get(StoredFile, stored_file_id)
            if not stored_file or stored_file.version_id != version_id:
                raise NotFoundError("Stored file not found in version")

        summary = data.pop("summary")
        run = ValidationRun(
            version_id=version_id,
            total_count=summary["total"],
            passed_count=summary["passed"],
            failed_count=summary["failed"],
            skipped_count=summary["skipped"],
            error_count=summary["errors"],
            warning_count=summary["warnings"],
            **data
        )
        self.database.add(run)
        self.database.commit()
        self.database.refresh(run)
        return run

    def list_for_version(self, version_id: UUID):
        if not self.database.get(Version, version_id):
            raise NotFoundError("Version not found")
        statement = (
            select(ValidationRun)
            .where(ValidationRun.version_id == version_id)
            .order_by(ValidationRun.created_at.desc())
        )
        return list(self.database.scalars(statement).all())

    def get(self, run_id: UUID):
        run = self.database.get(ValidationRun, run_id)
        if not run:
            raise NotFoundError("Validation run not found")
        return run
