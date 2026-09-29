from uuid import UUID

from fastapi import APIRouter, status

from s_usd_service.api.dependencies import CurrentUser, DatabaseSession
from s_usd_service.api.schemas.catalog import VersionCreate, VersionRead
from s_usd_service.database.repositories.authorization import AuthorizationRepository
from s_usd_service.database.repositories.catalog import CatalogRepository
from s_usd_service.domain.authorization import Permission
from s_usd_service.services.version_lifecycle import VersionLifecycleService

router = APIRouter(tags=["Versions"])


@router.post("/streams/{stream_id}/versions", response_model=VersionRead, status_code=status.HTTP_201_CREATED)
def create_version(stream_id: UUID, payload: VersionCreate, database: DatabaseSession, current_user: CurrentUser):
    AuthorizationRepository(database, current_user).require_stream(stream_id, Permission.CONTRIBUTE)
    return CatalogRepository(database).create_version(stream_id, payload.model_dump())


@router.get("/streams/{stream_id}/versions", response_model=list[VersionRead])
def list_versions(stream_id: UUID, database: DatabaseSession, current_user: CurrentUser):
    AuthorizationRepository(database, current_user).require_stream(stream_id)
    return CatalogRepository(database).list_versions(stream_id)


@router.get("/versions/{version_id}", response_model=VersionRead)
def get_version(version_id: UUID, database: DatabaseSession, current_user: CurrentUser):
    AuthorizationRepository(database, current_user).require_version(version_id)
    return CatalogRepository(database).get_version(version_id)


@router.post("/versions/{version_id}/publish", response_model=VersionRead)
def publish_version(version_id: UUID, database: DatabaseSession, current_user: CurrentUser):
    AuthorizationRepository(database, current_user).require_version(version_id, Permission.PUBLISH)
    return VersionLifecycleService(database).publish(version_id)


@router.post("/versions/{version_id}/deprecate", response_model=VersionRead)
def deprecate_version(version_id: UUID, database: DatabaseSession, current_user: CurrentUser):
    AuthorizationRepository(database, current_user).require_version(version_id, Permission.PUBLISH)
    return VersionLifecycleService(database).deprecate(version_id)
