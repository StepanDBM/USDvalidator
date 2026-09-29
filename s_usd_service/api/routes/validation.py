from uuid import UUID

from fastapi import APIRouter, status

from s_usd_service.api.dependencies import CurrentUser, DatabaseSession
from s_usd_service.api.schemas.validation import ValidationRunCreate, ValidationRunDetail, ValidationRunRead
from s_usd_service.database.repositories.authorization import AuthorizationRepository
from s_usd_service.database.repositories.validation import ValidationRunRepository
from s_usd_service.domain.authorization import Permission

router = APIRouter(tags=["Validation"])


@router.post(
    "/versions/{version_id}/validation-runs", response_model=ValidationRunDetail, status_code=status.HTTP_201_CREATED
)
def create_validation_run(
    version_id: UUID, payload: ValidationRunCreate, database: DatabaseSession, current_user: CurrentUser
):
    AuthorizationRepository(database, current_user).require_version(version_id, Permission.CONTRIBUTE)
    return ValidationRunRepository(database).create(version_id, payload.model_dump())


@router.get("/versions/{version_id}/validation-runs", response_model=list[ValidationRunRead])
def list_validation_runs(version_id: UUID, database: DatabaseSession, current_user: CurrentUser):
    AuthorizationRepository(database, current_user).require_version(version_id)
    return ValidationRunRepository(database).list_for_version(version_id)


@router.get("/validation-runs/{run_id}", response_model=ValidationRunDetail)
def get_validation_run(run_id: UUID, database: DatabaseSession, current_user: CurrentUser):
    AuthorizationRepository(database, current_user).require_validation_run(run_id)
    return ValidationRunRepository(database).get(run_id)
