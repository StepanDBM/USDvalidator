from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from s_usd_service.database.models import (
    Asset,
    Project,
    StoredFile,
    Stream,
    User,
    ValidationRun,
    Version,
    Workspace,
    WorkspaceMembership,
)
from s_usd_service.database.repositories.errors import ConflictError, NotFoundError
from s_usd_service.domain.authorization import Permission, WorkspaceRole, role_allows


class AuthorizationError(PermissionError):
    pass


class AuthorizationRepository:
    def __init__(self, database: Session, user: User):
        self.database = database
        self.user = user

    def list_workspaces(self):
        statement = (
            select(Workspace)
            .join(WorkspaceMembership)
            .where(WorkspaceMembership.user_id == self.user.id, Workspace.status == "active")
            .order_by(Workspace.code)
        )
        return list(self.database.scalars(statement).all())

    def require_workspace(self, workspace_id: UUID, permission: Permission = Permission.READ) -> WorkspaceMembership:
        statement = (
            select(WorkspaceMembership)
            .options(joinedload(WorkspaceMembership.workspace), joinedload(WorkspaceMembership.user))
            .where(
                WorkspaceMembership.workspace_id == workspace_id,
                WorkspaceMembership.user_id == self.user.id,
            )
        )
        membership = self.database.scalar(statement)
        if not membership or membership.workspace.status != "active":
            raise NotFoundError("Workspace not found")
        if not self.user.is_platform_admin and not role_allows(membership.role, permission):
            raise AuthorizationError("You do not have permission to perform this workspace operation.")
        return membership

    def require_project(self, project_id: UUID, permission: Permission = Permission.READ) -> WorkspaceMembership:
        workspace_id = self.database.scalar(select(Project.workspace_id).where(Project.id == project_id))
        if not workspace_id:
            raise NotFoundError("Project not found")
        return self.require_workspace(workspace_id, permission)

    def require_asset(self, asset_id: UUID, permission: Permission = Permission.READ) -> WorkspaceMembership:
        project_id = self.database.scalar(select(Asset.project_id).where(Asset.id == asset_id))
        if not project_id:
            raise NotFoundError("Asset not found")
        return self.require_project(project_id, permission)

    def require_stream(self, stream_id: UUID, permission: Permission = Permission.READ) -> WorkspaceMembership:
        asset_id = self.database.scalar(select(Stream.asset_id).where(Stream.id == stream_id))
        if not asset_id:
            raise NotFoundError("Stream not found")
        return self.require_asset(asset_id, permission)

    def require_version(self, version_id: UUID, permission: Permission = Permission.READ) -> WorkspaceMembership:
        stream_id = self.database.scalar(select(Version.stream_id).where(Version.id == version_id))
        if not stream_id:
            raise NotFoundError("Version not found")
        return self.require_stream(stream_id, permission)

    def require_file(self, file_id: UUID, permission: Permission = Permission.READ) -> WorkspaceMembership:
        version_id = self.database.scalar(select(StoredFile.version_id).where(StoredFile.id == file_id))
        if not version_id:
            raise NotFoundError("Stored file not found")
        return self.require_version(version_id, permission)

    def require_validation_run(self, run_id: UUID, permission: Permission = Permission.READ) -> WorkspaceMembership:
        version_id = self.database.scalar(select(ValidationRun.version_id).where(ValidationRun.id == run_id))
        if not version_id:
            raise NotFoundError("Validation run not found")
        return self.require_version(version_id, permission)

    def create_workspace(self, data) -> Workspace:
        if self.database.scalar(select(Workspace.id).where(Workspace.code == data["code"])):
            raise ConflictError(f"Workspace code '{data['code']}' already exists")
        workspace = Workspace(**data)
        self.database.add(workspace)
        self.database.flush()
        self.database.add(
            WorkspaceMembership(workspace_id=workspace.id, user_id=self.user.id, role=WorkspaceRole.OWNER.value)
        )
        self.database.commit()
        self.database.refresh(workspace)
        return workspace

    def list_memberships(self, workspace_id: UUID):
        self.require_workspace(workspace_id, Permission.READ)
        statement = (
            select(WorkspaceMembership)
            .options(joinedload(WorkspaceMembership.user))
            .where(WorkspaceMembership.workspace_id == workspace_id)
            .order_by(WorkspaceMembership.created_at, WorkspaceMembership.id)
        )
        return list(self.database.scalars(statement).unique().all())

    def add_member(self, workspace_id: UUID, email: str, role: WorkspaceRole):
        actor = self.require_workspace(workspace_id, Permission.MANAGE_MEMBERS)
        self._require_role_assignment(actor, role)
        normalized_email = email.strip().casefold()
        user = self.database.scalar(
            select(User).where(User.normalized_email == normalized_email, User.is_active.is_(True))
        )
        if not user:
            raise NotFoundError("Active user not found")
        if self.database.scalar(
            select(WorkspaceMembership.id).where(
                WorkspaceMembership.workspace_id == workspace_id, WorkspaceMembership.user_id == user.id
            )
        ):
            raise ConflictError("User is already a workspace member")
        membership = WorkspaceMembership(workspace_id=workspace_id, user_id=user.id, role=role.value)
        self.database.add(membership)
        self.database.commit()
        return self._get_membership(membership.id)

    def update_member(self, workspace_id: UUID, membership_id: UUID, role: WorkspaceRole):
        actor = self.require_workspace(workspace_id, Permission.MANAGE_MEMBERS)
        membership = self._get_workspace_membership(workspace_id, membership_id)
        self._require_role_assignment(actor, role)
        if membership.role == WorkspaceRole.OWNER.value and role is not WorkspaceRole.OWNER:
            self._require_not_final_owner(workspace_id)
        membership.role = role.value
        self.database.commit()
        return self._get_membership(membership.id)

    def remove_member(self, workspace_id: UUID, membership_id: UUID) -> None:
        actor = self.require_workspace(workspace_id, Permission.MANAGE_MEMBERS)
        membership = self._get_workspace_membership(workspace_id, membership_id)
        target_role = WorkspaceRole(membership.role)
        if target_role in {WorkspaceRole.OWNER, WorkspaceRole.ADMINISTRATOR}:
            if not role_allows(actor.role, Permission.MANAGE_ADMINISTRATORS):
                raise AuthorizationError("Only an Owner can remove Administrators or Owners.")
        if target_role is WorkspaceRole.OWNER:
            self._require_not_final_owner(workspace_id)
        self.database.delete(membership)
        self.database.commit()

    def _get_membership(self, membership_id: UUID):
        return self.database.scalar(
            select(WorkspaceMembership)
            .options(joinedload(WorkspaceMembership.user))
            .where(WorkspaceMembership.id == membership_id)
        )

    def _get_workspace_membership(self, workspace_id: UUID, membership_id: UUID):
        membership = self._get_membership(membership_id)
        if not membership or membership.workspace_id != workspace_id:
            raise NotFoundError("Workspace membership not found")
        return membership

    @staticmethod
    def _require_role_assignment(actor: WorkspaceMembership, role: WorkspaceRole) -> None:
        if role in {WorkspaceRole.OWNER, WorkspaceRole.ADMINISTRATOR} and not role_allows(
            actor.role, Permission.MANAGE_ADMINISTRATORS
        ):
            raise AuthorizationError("Only an Owner can assign Administrator or Owner roles.")

    def _require_not_final_owner(self, workspace_id: UUID) -> None:
        owner_count = self.database.scalar(
            select(func.count(WorkspaceMembership.id)).where(
                WorkspaceMembership.workspace_id == workspace_id,
                WorkspaceMembership.role == WorkspaceRole.OWNER.value,
            )
        )
        if owner_count <= 1:
            raise ConflictError("A workspace must retain at least one Owner.")
