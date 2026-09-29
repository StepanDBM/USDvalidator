from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from s_usd_service.api.schemas.common import ApiModel
from s_usd_service.domain.projects import PROJECT_STATUSES


class ProjectCreate(ApiModel):
    workspace_id: UUID | None = None
    code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=128)
    description: str = Field(default="", max_length=2000)
    default_validation_profile: str = Field(default="default", min_length=1, max_length=128)

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value):
        return value.strip().upper()

    @field_validator("name", "default_validation_profile")
    @classmethod
    def strip_required_text(cls, value):
        return value.strip()


class ProjectUpdate(ApiModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=2000)
    status: str | None = None
    default_validation_profile: str | None = Field(default=None, min_length=1, max_length=128)

    @field_validator("name", "default_validation_profile")
    @classmethod
    def strip_optional_text(cls, value):
        return value.strip() if value is not None else value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if value is not None and value not in PROJECT_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(PROJECT_STATUSES)}")
        return value


class ProjectRead(ProjectCreate):
    id: UUID
    workspace_id: UUID
    created_by_user_id: UUID | None
    status: str
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AssetCreate(ApiModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    asset_type: str = Field(min_length=1, max_length=32)
    description: str = Field(default="", max_length=2000)

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value):
        return value.strip().lower()


class AssetRead(AssetCreate):
    id: UUID
    project_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime


class StreamCreate(ApiModel):
    name: str = Field(min_length=1, max_length=64)
    description: str = Field(default="", max_length=2000)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value):
        return value.strip().lower()


class StreamRead(StreamCreate):
    id: UUID
    asset_id: UUID
    created_at: datetime
    updated_at: datetime


class VersionCreate(ApiModel):
    comment: str = Field(default="", max_length=4000)


class VersionRead(VersionCreate):
    id: UUID
    stream_id: UUID
    number: int
    status: str
    published_content_fingerprint: str | None = None
    created_at: datetime
    updated_at: datetime
