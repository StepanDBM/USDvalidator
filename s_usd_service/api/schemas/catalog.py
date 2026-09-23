from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from s_usd_service.api.schemas.common import ApiModel


class ProjectCreate(ApiModel):
    code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=128)
    description: str = Field(default="", max_length=2000)

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value):
        return value.strip().upper()


class ProjectRead(ProjectCreate):
    id: UUID
    status: str
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
