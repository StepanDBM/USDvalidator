"""Add version-content fingerprints.

Revision ID: 0004
Revises: 0003
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("validation_runs") as batch:
        batch.add_column(sa.Column(
            "content_fingerprint", sa.String(length=64), nullable=False,
            server_default=""
        ))
    with op.batch_alter_table("versions") as batch:
        batch.add_column(sa.Column(
            "published_content_fingerprint", sa.String(length=64), nullable=True
        ))


def downgrade():
    with op.batch_alter_table("versions") as batch:
        batch.drop_column("published_content_fingerprint")
    with op.batch_alter_table("validation_runs") as batch:
        batch.drop_column("content_fingerprint")
