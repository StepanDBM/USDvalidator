from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from s_usd_service.database.base_class import Base
from s_usd_service.database.models.mixins import IdMixin, TimestampMixin


class Stream(IdMixin, TimestampMixin, Base):
    __tablename__ = "streams"
    __table_args__ = (UniqueConstraint("asset_id", "name", name="uq_stream_asset_name"),)

    asset_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("assets.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text, default="")
    asset: Mapped["Asset"] = relationship(back_populates="streams")
    versions: Mapped[list["Version"]] = relationship(back_populates="stream", cascade="all, delete-orphan")
