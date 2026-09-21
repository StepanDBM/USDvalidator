"""Add validation runs.

Revision ID: 0003
Revises: 0002
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "validation_runs",
        sa.Column("version_id", sa.Uuid(), nullable=False),
        sa.Column("stored_file_id", sa.Uuid(), nullable=True),
        sa.Column("profile_name", sa.String(128), nullable=False),
        sa.Column("report_schema_version", sa.String(32), nullable=False),
        sa.Column("tool_name", sa.String(128), nullable=False),
        sa.Column("tool_version", sa.String(64), nullable=False),
        sa.Column("configuration_fingerprint", sa.String(64), nullable=False),
        sa.Column("check_catalog_fingerprint", sa.String(64), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_seconds", sa.Float(), nullable=False),
        sa.Column("publish_passed", sa.Boolean(), nullable=False),
        sa.Column("total_count", sa.Integer(), nullable=False),
        sa.Column("passed_count", sa.Integer(), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("skipped_count", sa.Integer(), nullable=False),
        sa.Column("error_count", sa.Integer(), nullable=False),
        sa.Column("warning_count", sa.Integer(), nullable=False),
        sa.Column("report", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["stored_file_id"], ["stored_files.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["version_id"], ["versions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_validation_runs_version_id", "validation_runs", ["version_id"])
    op.create_index("ix_validation_runs_stored_file_id", "validation_runs", ["stored_file_id"])
    op.create_index(
        "ix_validation_runs_version_created_at",
        "validation_runs",
        ["version_id", "created_at"]
    )


def downgrade():
    op.drop_index("ix_validation_runs_version_created_at", table_name="validation_runs")
    op.drop_index("ix_validation_runs_stored_file_id", table_name="validation_runs")
    op.drop_index("ix_validation_runs_version_id", table_name="validation_runs")
    op.drop_table("validation_runs")
