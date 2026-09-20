from uuid import UUID

from s_usd_service.api.schemas.common import ApiModel


class FileDeletionResponse(ApiModel):
    file_id: UUID
    storage_key: str
    object_existed: bool
    metadata_deleted: bool


class ReconciliationResponse(ApiModel):
    consistent: bool
    database_records: int
    storage_objects: int
    missing_database_objects: list[str]
    orphaned_storage_objects: list[str]
    restored_records: list[str]
    marked_missing_records: list[str]
    deleted_orphaned_objects: list[str]
