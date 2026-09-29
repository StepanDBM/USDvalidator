from datetime import datetime
from uuid import UUID

from pydantic import Field

from s_usd_service.api.schemas.common import ApiModel


class ValidationJobCreate(ApiModel):
    stored_file_id: UUID
    idempotency_key: str = Field(min_length=1, max_length=128)
    profile_name: str = Field(default="default", min_length=1, max_length=128)


class ValidationJobRead(ApiModel):
    id: UUID
    workspace_id: UUID
    version_id: UUID
    stored_file_id: UUID
    requested_by_user_id: UUID
    validation_run_id: UUID | None
    idempotency_key: str
    profile_name: str
    status: str
    progress_current: int
    progress_total: int
    attempt_count: int
    maximum_attempts: int
    requested_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    heartbeat_at: datetime | None
    next_attempt_at: datetime | None
    error_code: str
    error_message: str
    created_at: datetime
    updated_at: datetime
