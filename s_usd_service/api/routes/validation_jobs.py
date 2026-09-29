from uuid import UUID

from fastapi import APIRouter, Response, status

from s_usd_service.api.dependencies import CurrentUser, DatabaseSession
from s_usd_service.api.schemas.validation_jobs import ValidationJobCreate, ValidationJobRead
from s_usd_service.config import get_settings
from s_usd_service.database.repositories.authorization import AuthorizationRepository
from s_usd_service.database.repositories.validation_jobs import ValidationJobRepository
from s_usd_service.domain.authorization import Permission

router = APIRouter(tags=["Validation Jobs"])


@router.post("/versions/{version_id}/validation-jobs", response_model=ValidationJobRead)
def create_validation_job(
    version_id: UUID,
    payload: ValidationJobCreate,
    response: Response,
    database: DatabaseSession,
    current_user: CurrentUser,
):
    membership = AuthorizationRepository(database, current_user).require_version(version_id, Permission.CONTRIBUTE)
    job, created = ValidationJobRepository(database).create(
        workspace_id=membership.workspace_id,
        version_id=version_id,
        stored_file_id=payload.stored_file_id,
        user_id=current_user.id,
        idempotency_key=payload.idempotency_key,
        profile_name=payload.profile_name,
        maximum_attempts=get_settings().validation_job_maximum_attempts,
    )
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return job


@router.get("/versions/{version_id}/validation-jobs", response_model=list[ValidationJobRead])
def list_validation_jobs(version_id: UUID, database: DatabaseSession, current_user: CurrentUser):
    AuthorizationRepository(database, current_user).require_version(version_id)
    return ValidationJobRepository(database).list_for_version(version_id)


@router.get("/validation-jobs/{job_id}", response_model=ValidationJobRead)
def get_validation_job(job_id: UUID, database: DatabaseSession, current_user: CurrentUser):
    job = ValidationJobRepository(database).get(job_id)
    AuthorizationRepository(database, current_user).require_version(job.version_id)
    return job


@router.post("/validation-jobs/{job_id}/cancel", response_model=ValidationJobRead)
def cancel_validation_job(job_id: UUID, database: DatabaseSession, current_user: CurrentUser):
    job = ValidationJobRepository(database).get(job_id)
    AuthorizationRepository(database, current_user).require_version(job.version_id, Permission.CONTRIBUTE)
    return ValidationJobRepository(database).request_cancellation(job_id)
