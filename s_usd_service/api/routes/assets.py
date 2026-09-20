from uuid import UUID

from fastapi import APIRouter, status

from s_usd_service.api.dependencies import DatabaseSession
from s_usd_service.api.schemas.catalog import AssetCreate, AssetRead
from s_usd_service.database.repositories.catalog import CatalogRepository

router = APIRouter(tags=["Assets"])


@router.post("/projects/{project_id}/assets", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(project_id: UUID, payload: AssetCreate, database: DatabaseSession):
    return CatalogRepository(database).create_asset(project_id, payload.model_dump())


@router.get("/projects/{project_id}/assets", response_model=list[AssetRead])
def list_assets(project_id: UUID, database: DatabaseSession):
    return CatalogRepository(database).list_assets(project_id)


@router.get("/assets/{asset_id}", response_model=AssetRead)
def get_asset(asset_id: UUID, database: DatabaseSession):
    return CatalogRepository(database).get_asset(asset_id)
