from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from s_usd_service.database.base_class import Base
from s_usd_service.database.models.mixins import IdMixin, TimestampMixin


class StoredFile(IdMixin, TimestampMixin, Base):
    __tablename__ = "stored_files"
    __table_args__ = (
        UniqueConstraint("version_id", "relative_path", name="uq_stored_file_version_relative_path"),
        UniqueConstraint("storage_key", name="uq_stored_file_storage_key"),
    )

    version_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("versions.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String(32), default="other")
    original_name: Mapped[str] = mapped_column(String(255))
    relative_path: Mapped[str] = mapped_column(String(1024))
    storage_key: Mapped[str] = mapped_column(String(2048))
    content_type: Mapped[str] = mapped_column(String(255), default="application/octet-stream")
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), default="available")
    version: Mapped["Version"] = relationship(back_populates="files")
