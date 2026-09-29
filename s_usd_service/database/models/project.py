from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from s_usd_service.database.base_class import Base
from s_usd_service.database.models.mixins import IdMixin, TimestampMixin

if TYPE_CHECKING:
    from s_usd_service.database.models.asset import Asset
    from s_usd_service.database.models.user import User
    from s_usd_service.database.models.workspace import Workspace


class Project(IdMixin, TimestampMixin, Base):
    __tablename__ = "projects"
    __table_args__ = (UniqueConstraint("workspace_id", "code", name="uq_projects_workspace_code"),)

    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="RESTRICT"), index=True)
    created_by_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    code: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="active")
    workspace: Mapped[Workspace] = relationship(back_populates="projects")
    created_by: Mapped[User | None] = relationship()
    assets: Mapped[list[Asset]] = relationship(back_populates="project", cascade="all, delete-orphan")
