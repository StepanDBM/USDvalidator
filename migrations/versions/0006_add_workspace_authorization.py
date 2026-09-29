"""Add workspace authorization and project ownership.

Revision ID: 0006
Revises: 0005
"""

from datetime import datetime, timezone
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def _database_uuid(connection, value):
    return value.hex if connection.dialect.name == "sqlite" else value


def upgrade():
    op.create_table(
        "workspaces",
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_workspaces_code", "workspaces", ["code"])
    op.create_index("ix_workspaces_status", "workspaces", ["status"])
    op.create_table(
        "workspace_memberships",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "user_id", name="uq_workspace_membership_user"),
    )
    op.create_index("ix_workspace_memberships_role", "workspace_memberships", ["role"])
    op.create_index("ix_workspace_memberships_user_id", "workspace_memberships", ["user_id"])
    op.create_index("ix_workspace_memberships_workspace_id", "workspace_memberships", ["workspace_id"])

    with op.batch_alter_table("projects") as batch:
        batch.add_column(sa.Column("workspace_id", sa.Uuid(), nullable=True))
        batch.add_column(sa.Column("created_by_user_id", sa.Uuid(), nullable=True))
        batch.create_foreign_key("fk_projects_workspace", "workspaces", ["workspace_id"], ["id"], ondelete="RESTRICT")
        batch.create_foreign_key("fk_projects_creator", "users", ["created_by_user_id"], ["id"], ondelete="SET NULL")

    connection = op.get_bind()
    project_count = connection.scalar(sa.text("SELECT COUNT(*) FROM projects"))
    if project_count:
        now = datetime.now(timezone.utc)
        user_id = uuid4()
        workspace_id = uuid4()
        membership_id = uuid4()
        connection.execute(
            sa.text(
                "INSERT INTO users (email, normalized_email, display_name, password_hash, is_active, "
                "is_platform_admin, id, created_at, updated_at) "
                "VALUES (:email, :email, :name, :password_hash, :active, :admin, :id, :created, :updated)"
            ),
            {
                "email": "migration-bootstrap@s-usdv.invalid",
                "name": "Migration Bootstrap User",
                "password_hash": "!migration-bootstrap-account-disabled!",
                "active": False,
                "admin": False,
                "id": _database_uuid(connection, user_id),
                "created": now,
                "updated": now,
            },
        )
        connection.execute(
            sa.text(
                "INSERT INTO workspaces (code, name, description, status, id, created_at, updated_at) "
                "VALUES (:code, :name, :description, :status, :id, :created, :updated)"
            ),
            {
                "code": "LEGACY",
                "name": "Legacy Projects",
                "description": "Workspace created automatically for pre-v0.2 projects.",
                "status": "active",
                "id": _database_uuid(connection, workspace_id),
                "created": now,
                "updated": now,
            },
        )
        connection.execute(
            sa.text(
                "INSERT INTO workspace_memberships (workspace_id, user_id, role, id, created_at, updated_at) "
                "VALUES (:workspace_id, :user_id, :role, :id, :created, :updated)"
            ),
            {
                "workspace_id": _database_uuid(connection, workspace_id),
                "user_id": _database_uuid(connection, user_id),
                "role": "owner",
                "id": _database_uuid(connection, membership_id),
                "created": now,
                "updated": now,
            },
        )
        connection.execute(
            sa.text("UPDATE projects SET workspace_id = :workspace_id, created_by_user_id = :user_id"),
            {
                "workspace_id": _database_uuid(connection, workspace_id),
                "user_id": _database_uuid(connection, user_id),
            },
        )

    with op.batch_alter_table("projects") as batch:
        batch.alter_column("workspace_id", existing_type=sa.Uuid(), nullable=False)
        batch.create_index("ix_projects_workspace_id", ["workspace_id"])
        batch.drop_index("ix_projects_code")
        batch.create_index("ix_projects_code", ["code"], unique=False)
        batch.create_unique_constraint("uq_projects_workspace_code", ["workspace_id", "code"])


def downgrade():
    with op.batch_alter_table("projects") as batch:
        batch.drop_constraint("uq_projects_workspace_code", type_="unique")
        batch.drop_index("ix_projects_code")
        batch.create_index("ix_projects_code", ["code"], unique=True)
        batch.drop_index("ix_projects_workspace_id")
        batch.drop_constraint("fk_projects_creator", type_="foreignkey")
        batch.drop_constraint("fk_projects_workspace", type_="foreignkey")
        batch.drop_column("created_by_user_id")
        batch.drop_column("workspace_id")
    op.drop_table("workspace_memberships")
    op.drop_table("workspaces")
