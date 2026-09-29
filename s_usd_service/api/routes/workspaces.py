from uuid import UUID

from fastapi import APIRouter, status

from s_usd_service.api.dependencies import CurrentUser, DatabaseSession
from s_usd_service.api.schemas.workspaces import (
    MembershipCreate,
    MembershipRead,
    MembershipUpdate,
    WorkspaceCreate,
    WorkspaceRead,
)
from s_usd_service.database.repositories.authorization import AuthorizationRepository

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post("", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
def create_workspace(payload: WorkspaceCreate, database: DatabaseSession, current_user: CurrentUser):
    return AuthorizationRepository(database, current_user).create_workspace(payload.model_dump())


@router.get("", response_model=list[WorkspaceRead])
def list_workspaces(database: DatabaseSession, current_user: CurrentUser):
    return AuthorizationRepository(database, current_user).list_workspaces()


@router.get("/{workspace_id}", response_model=WorkspaceRead)
def get_workspace(workspace_id: UUID, database: DatabaseSession, current_user: CurrentUser):
    return AuthorizationRepository(database, current_user).require_workspace(workspace_id).workspace


@router.get("/{workspace_id}/members", response_model=list[MembershipRead])
def list_members(workspace_id: UUID, database: DatabaseSession, current_user: CurrentUser):
    return AuthorizationRepository(database, current_user).list_memberships(workspace_id)


@router.post("/{workspace_id}/members", response_model=MembershipRead, status_code=status.HTTP_201_CREATED)
def add_member(workspace_id: UUID, payload: MembershipCreate, database: DatabaseSession, current_user: CurrentUser):
    return AuthorizationRepository(database, current_user).add_member(workspace_id, payload.email, payload.role)


@router.patch("/{workspace_id}/members/{membership_id}", response_model=MembershipRead)
def update_member(
    workspace_id: UUID,
    membership_id: UUID,
    payload: MembershipUpdate,
    database: DatabaseSession,
    current_user: CurrentUser,
):
    return AuthorizationRepository(database, current_user).update_member(workspace_id, membership_id, payload.role)


@router.delete("/{workspace_id}/members/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(workspace_id: UUID, membership_id: UUID, database: DatabaseSession, current_user: CurrentUser):
    AuthorizationRepository(database, current_user).remove_member(workspace_id, membership_id)
