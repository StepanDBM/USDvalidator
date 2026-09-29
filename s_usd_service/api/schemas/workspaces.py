from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from s_usd_service.api.schemas.auth import UserRead
from s_usd_service.api.schemas.common import ApiModel
from s_usd_service.domain.authorization import WorkspaceRole


class WorkspaceCreate(ApiModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    description: str = Field(default="", max_length=2000)

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip().upper()


class WorkspaceRead(WorkspaceCreate):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime


class MembershipCreate(ApiModel):
    email: EmailStr
    role: WorkspaceRole = WorkspaceRole.VIEWER


class MembershipUpdate(ApiModel):
    role: WorkspaceRole


class MembershipRead(ApiModel):
    id: UUID
    workspace_id: UUID
    role: WorkspaceRole
    user: UserRead
    created_at: datetime
    updated_at: datetime
