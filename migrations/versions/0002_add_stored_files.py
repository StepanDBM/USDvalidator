"""Add stored files.

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "stored_files",
        sa.Column("version_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("relative_path", sa.String(length=1024), nullable=False),
        sa.Column("storage_key", sa.String(length=2048), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["version_id"], ["versions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key", name="uq_stored_file_storage_key"),
        sa.UniqueConstraint("version_id", "relative_path", name="uq_stored_file_version_relative_path")
    )
    op.create_index("ix_stored_files_sha256", "stored_files", ["sha256"], unique=False)
    op.create_index("ix_stored_files_version_id", "stored_files", ["version_id"], unique=False)


def downgrade():
    op.drop_index("ix_stored_files_version_id", table_name="stored_files")
    op.drop_index("ix_stored_files_sha256", table_name="stored_files")
    op.drop_table("stored_files")
