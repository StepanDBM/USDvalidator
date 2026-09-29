from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from s_usd_service.database.base_class import Base
from s_usd_service.database.models.mixins import IdMixin, TimestampMixin

if TYPE_CHECKING:
    from s_usd_service.database.models.refresh_session import RefreshSession
    from s_usd_service.database.models.workspace_membership import WorkspaceMembership


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    normalized_email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(128))
    password_hash: Mapped[str] = mapped_column(String(512))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_platform_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    refresh_sessions: Mapped[list[RefreshSession]] = relationship(back_populates="user", cascade="all, delete-orphan")
    workspace_memberships: Mapped[list[WorkspaceMembership]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
