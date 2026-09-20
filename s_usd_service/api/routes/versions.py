from uuid import UUID

from fastapi import APIRouter, status

from s_usd_service.api.dependencies import DatabaseSession
from s_usd_service.api.schemas.catalog import VersionCreate, VersionRead
from s_usd_service.database.repositories.catalog import CatalogRepository

router = APIRouter(tags=["Versions"])


@router.post("/streams/{stream_id}/versions", response_model=VersionRead, status_code=status.HTTP_201_CREATED)
def create_version(stream_id: UUID, payload: VersionCreate, database: DatabaseSession):
    return CatalogRepository(database).create_version(stream_id, payload.model_dump())


@router.get("/streams/{stream_id}/versions", response_model=list[VersionRead])
def list_versions(stream_id: UUID, database: DatabaseSession):
    return CatalogRepository(database).list_versions(stream_id)


@router.get("/versions/{version_id}", response_model=VersionRead)
def get_version(version_id: UUID, database: DatabaseSession):
    return CatalogRepository(database).get_version(version_id)
