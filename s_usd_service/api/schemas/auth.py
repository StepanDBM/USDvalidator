from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from s_usd_service.api.schemas.common import ApiModel


class RegisterRequest(ApiModel):
    email: EmailStr
    display_name: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=12, max_length=1024)

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: str) -> str:
        return value.strip()


class LoginRequest(ApiModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=1024)
    client_name: str = Field(default="", max_length=128)
    client_fingerprint: str = Field(default="", max_length=128)


class RefreshRequest(ApiModel):
    refresh_token: str = Field(min_length=1, max_length=2048)


class LogoutRequest(RefreshRequest):
    pass


class UserRead(ApiModel):
    id: UUID
    email: EmailStr
    display_name: str
    is_active: bool
    is_platform_admin: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None


class TokenPair(ApiModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_expires_at: datetime
    refresh_expires_at: datetime
    user: UserRead
