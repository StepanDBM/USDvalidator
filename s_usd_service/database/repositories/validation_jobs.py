from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from s_usd_service.database.models import StoredFile, ValidationJob, Version
from s_usd_service.database.repositories.errors import ConflictError, NotFoundError
from s_usd_service.domain.validation_jobs import TERMINAL_JOB_STATUSES, ValidationJobStatus


def utc_now():
    return datetime.now(timezone.utc)


class ValidationJobRepository:
    def __init__(self, database: Session):
        self.database = database

    def create(
        self, *, workspace_id, version_id, stored_file_id, user_id, idempotency_key, profile_name, maximum_attempts
    ):
        existing = self.database.scalar(
            select(ValidationJob).where(
                ValidationJob.workspace_id == workspace_id,
                ValidationJob.requested_by_user_id == user_id,
                ValidationJob.idempotency_key == idempotency_key,
            )
        )
        if existing:
            return existing, False

        version = self.database.get(Version, version_id)
        stored_file = self.database.get(StoredFile, stored_file_id)
        if not version:
            raise NotFoundError("Version not found")
        if not stored_file or stored_file.version_id != version_id:
            raise NotFoundError("Stored file not found in version")
        if stored_file.role != "root_layer" or stored_file.status != "available":
            raise ConflictError("Validation jobs require an available root_layer file")

        job = ValidationJob(
            workspace_id=workspace_id,
            version_id=version_id,
            stored_file_id=stored_file_id,
            requested_by_user_id=user_id,
            idempotency_key=idempotency_key,
            profile_name=profile_name,
            maximum_attempts=maximum_attempts,
            requested_at=utc_now(),
        )
        self.database.add(job)
        self.database.commit()
        self.database.refresh(job)
        return job, True

    def get(self, job_id: UUID):
        job = self.database.scalar(
            select(ValidationJob)
            .options(joinedload(ValidationJob.version), joinedload(ValidationJob.stored_file))
            .where(ValidationJob.id == job_id)
        )
        if not job:
            raise NotFoundError("Validation job not found")
        return job

    def list_for_version(self, version_id: UUID):
        return tuple(
            self.database.scalars(
                select(ValidationJob)
                .where(ValidationJob.version_id == version_id)
                .order_by(ValidationJob.requested_at.desc())
            )
        )

    def claim_next(self):
        now = utc_now()
        job = self.database.scalar(
            select(ValidationJob)
            .where(
                ValidationJob.status == ValidationJobStatus.PENDING.value,
                or_(ValidationJob.next_attempt_at.is_(None), ValidationJob.next_attempt_at <= now),
            )
            .order_by(ValidationJob.requested_at, ValidationJob.id)
            .limit(1)
        )
        if not job:
            return None
        job.status = ValidationJobStatus.RUNNING.value
        job.started_at = job.started_at or now
        job.heartbeat_at = now
        job.attempt_count += 1
        job.error_code = ""
        job.error_message = ""
        self.database.commit()
        self.database.refresh(job)
        return job

    def request_cancellation(self, job_id: UUID):
        job = self.get(job_id)
        if job.status in TERMINAL_JOB_STATUSES:
            return job
        now = utc_now()
        if job.status == ValidationJobStatus.PENDING.value:
            job.status = ValidationJobStatus.CANCELLED.value
            job.cancelled_at = now
            job.completed_at = now
        else:
            job.status = ValidationJobStatus.CANCELLING.value
        self.database.commit()
        self.database.refresh(job)
        return job
