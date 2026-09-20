from uuid import UUID

from fastapi import APIRouter, status

from s_usd_service.api.dependencies import DatabaseSession
from s_usd_service.api.schemas.catalog import StreamCreate, StreamRead
from s_usd_service.database.repositories.catalog import CatalogRepository

router = APIRouter(tags=["Streams"])


@router.post("/assets/{asset_id}/streams", response_model=StreamRead, status_code=status.HTTP_201_CREATED)
def create_stream(asset_id: UUID, payload: StreamCreate, database: DatabaseSession):
    return CatalogRepository(database).create_stream(asset_id, payload.model_dump())


@router.get("/assets/{asset_id}/streams", response_model=list[StreamRead])
def list_streams(asset_id: UUID, database: DatabaseSession):
    return CatalogRepository(database).list_streams(asset_id)


@router.get("/streams/{stream_id}", response_model=StreamRead)
def get_stream(stream_id: UUID, database: DatabaseSession):
    return CatalogRepository(database).get_stream(stream_id)
