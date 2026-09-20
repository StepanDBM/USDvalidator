"""Create initial catalog.

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("projects", sa.Column("code", sa.String(32), nullable=False), sa.Column("name", sa.String(128), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("id", sa.Uuid(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_projects_code", "projects", ["code"], unique=True)
    op.create_table("assets", sa.Column("project_id", sa.Uuid(), nullable=False), sa.Column("code", sa.String(64), nullable=False), sa.Column("name", sa.String(128), nullable=False), sa.Column("asset_type", sa.String(32), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("id", sa.Uuid(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("project_id", "code", name="uq_asset_project_code"))
    op.create_index("ix_assets_project_id", "assets", ["project_id"])
    op.create_table("streams", sa.Column("asset_id", sa.Uuid(), nullable=False), sa.Column("name", sa.String(64), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("id", sa.Uuid(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("asset_id", "name", name="uq_stream_asset_name"))
    op.create_index("ix_streams_asset_id", "streams", ["asset_id"])
    op.create_table("versions", sa.Column("stream_id", sa.Uuid(), nullable=False), sa.Column("number", sa.Integer(), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("comment", sa.Text(), nullable=False), sa.Column("id", sa.Uuid(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["stream_id"], ["streams.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("stream_id", "number", name="uq_version_stream_number"))
    op.create_index("ix_versions_stream_id", "versions", ["stream_id"])


def downgrade():
    op.drop_table("versions")
    op.drop_table("streams")
    op.drop_table("assets")
    op.drop_table("projects")
