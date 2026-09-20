from datetime import datetime
from uuid import UUID

from s_usd_service.api.schemas.common import ApiModel


class StoredFileRead(ApiModel):
    id: UUID
    version_id: UUID
    role: str
    original_name: str
    relative_path: str
    storage_key: str
    content_type: str
    size_bytes: int
    sha256: str
    status: str
    created_at: datetime
    updated_at: datetime
    content_url: str


class StoredFileList(ApiModel):
    items: list[StoredFileRead]
    count: int
