"""Add project administration fields.

Revision ID: 0008
Revises: 0007
"""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("projects") as batch:
        batch.add_column(
            sa.Column("default_validation_profile", sa.String(128), nullable=False, server_default="default")
        )
        batch.add_column(sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True))
        batch.create_index("ix_projects_status", ["status"])


def downgrade():
    with op.batch_alter_table("projects") as batch:
        batch.drop_index("ix_projects_status")
        batch.drop_column("archived_at")
        batch.drop_column("default_validation_profile")
