from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from s_usd_service.database.base_class import Base
from s_usd_service.database.models.mixins import IdMixin, TimestampMixin

if TYPE_CHECKING:
    from s_usd_service.database.models.stored_file import StoredFile
    from s_usd_service.database.models.user import User
    from s_usd_service.database.models.validation_run import ValidationRun
    from s_usd_service.database.models.version import Version
    from s_usd_service.database.models.workspace import Workspace


class ValidationJob(IdMixin, TimestampMixin, Base):
    __tablename__ = "validation_jobs"
    __table_args__ = (
        UniqueConstraint("workspace_id", "requested_by_user_id", "idempotency_key", name="uq_validation_job_request"),
        Index("ix_validation_jobs_status_requested", "status", "requested_at"),
    )

    workspace_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("versions.id", ondelete="CASCADE"), index=True)
    stored_file_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("stored_files.id", ondelete="CASCADE"), index=True)
    requested_by_user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    validation_run_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("validation_runs.id", ondelete="SET NULL"), nullable=True, unique=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(128))
    profile_name: Mapped[str] = mapped_column(String(128), default="default")
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    progress_current: Mapped[int] = mapped_column(Integer, default=0)
    progress_total: Mapped[int] = mapped_column(Integer, default=1)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    maximum_attempts: Mapped[int] = mapped_column(Integer, default=3)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str] = mapped_column(String(64), default="")
    error_message: Mapped[str] = mapped_column(Text, default="")

    workspace: Mapped["Workspace"] = relationship()
    version: Mapped["Version"] = relationship()
    stored_file: Mapped["StoredFile"] = relationship()
    requested_by: Mapped["User"] = relationship()
    validation_run: Mapped["ValidationRun | None"] = relationship()
