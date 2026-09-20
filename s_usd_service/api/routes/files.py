from uuid import UUID

from fastapi import APIRouter

from s_usd_service.api.dependencies import DatabaseSession, ObjectStorageDependency
from s_usd_service.api.schemas.storage import FileDeletionResponse
from s_usd_service.services.file_lifecycle import FileLifecycleService

router = APIRouter(prefix="/files", tags=["Files"])


@router.delete("/{file_id}", response_model=FileDeletionResponse)
def delete_file(file_id: UUID, database: DatabaseSession, storage: ObjectStorageDependency):
    return FileLifecycleService(database, storage).delete(file_id)
