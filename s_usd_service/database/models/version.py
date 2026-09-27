from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from s_usd_service.database.base_class import Base
from s_usd_service.database.models.mixins import IdMixin, TimestampMixin

if TYPE_CHECKING:
    from s_usd_service.database.models.stored_file import StoredFile
    from s_usd_service.database.models.stream import Stream
    from s_usd_service.database.models.validation_run import ValidationRun


class Version(IdMixin, TimestampMixin, Base):
    __tablename__ = "versions"
    __table_args__ = (UniqueConstraint("stream_id", "number", name="uq_version_stream_number"),)

    stream_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("streams.id", ondelete="CASCADE"), index=True)
    number: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    comment: Mapped[str] = mapped_column(Text, default="")
    published_content_fingerprint: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    stream: Mapped["Stream"] = relationship(back_populates="versions")
    files: Mapped[list["StoredFile"]] = relationship(back_populates="version", cascade="all, delete-orphan")
    validation_runs: Mapped[list["ValidationRun"]] = relationship(
        back_populates="version", cascade="all, delete-orphan"
    )
