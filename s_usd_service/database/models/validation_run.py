from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from s_usd_service.database.base_class import Base
from s_usd_service.database.models.mixins import IdMixin, TimestampMixin


class ValidationRun(IdMixin, TimestampMixin, Base):
    __tablename__ = "validation_runs"

    version_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("versions.id", ondelete="CASCADE"), index=True
    )
    stored_file_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("stored_files.id", ondelete="SET NULL"), nullable=True, index=True
    )
    profile_name: Mapped[str] = mapped_column(String(128))
    report_schema_version: Mapped[str] = mapped_column(String(32))
    tool_name: Mapped[str] = mapped_column(String(128))
    tool_version: Mapped[str] = mapped_column(String(64))
    configuration_fingerprint: Mapped[str] = mapped_column(String(64), default="")
    check_catalog_fingerprint: Mapped[str] = mapped_column(String(64), default="")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    publish_passed: Mapped[bool] = mapped_column(Boolean)
    total_count: Mapped[int] = mapped_column(Integer, default=0)
    passed_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, default=0)
    report: Mapped[dict[str, Any]] = mapped_column(JSON)

    version: Mapped["Version"] = relationship(back_populates="validation_runs")
    stored_file: Mapped["StoredFile"] = relationship(back_populates="validation_runs")
