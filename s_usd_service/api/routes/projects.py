from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from s_usd_service.api.dependencies import CurrentUser, DatabaseSession
from s_usd_service.api.schemas.catalog import ProjectCreate, ProjectRead, ProjectUpdate
from s_usd_service.database.repositories.authorization import AuthorizationRepository
from s_usd_service.database.repositories.catalog import CatalogRepository
from s_usd_service.domain.authorization import Permission
from s_usd_service.domain.projects import PROJECT_STATUSES

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, database: DatabaseSession, current_user: CurrentUser):
    access = AuthorizationRepository(database, current_user)
    workspace_id = payload.workspace_id
    if workspace_id is None:
        workspaces = access.list_workspaces()
        if len(workspaces) != 1:
            raise HTTPException(
                status_code=422, detail="workspace_id is required when multiple workspaces are available."
            )
        workspace_id = workspaces[0].id
    access.require_workspace(workspace_id, Permission.MANAGE_PROJECTS)
    data = payload.model_dump(exclude={"workspace_id"})
    return CatalogRepository(database).create_project(workspace_id, current_user.id, data)


@router.get("", response_model=list[ProjectRead])
def list_projects(
    database: DatabaseSession,
    current_user: CurrentUser,
    workspace_id: UUID | None = None,
    project_status: str | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None, max_length=128),
    created_by_user_id: UUID | None = None,
):
    if project_status is not None and project_status not in PROJECT_STATUSES:
        raise HTTPException(status_code=422, detail=f"status must be one of: {', '.join(PROJECT_STATUSES)}")
    if workspace_id is not None:
        AuthorizationRepository(database, current_user).require_workspace(workspace_id)
    return CatalogRepository(database).list_projects(
        current_user.id,
        workspace_id=workspace_id,
        status=project_status,
        search=search,
        created_by_user_id=created_by_user_id,
    )


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: UUID, database: DatabaseSession, current_user: CurrentUser):
    AuthorizationRepository(database, current_user).require_project(project_id)
    return CatalogRepository(database).get_project(project_id)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: UUID, payload: ProjectUpdate, database: DatabaseSession, current_user: CurrentUser
):
    AuthorizationRepository(database, current_user).require_project(project_id, Permission.MANAGE_PROJECTS)
    return CatalogRepository(database).update_project(project_id, payload.model_dump(exclude_unset=True))


@router.post("/{project_id}/archive", response_model=ProjectRead)
def archive_project(project_id: UUID, database: DatabaseSession, current_user: CurrentUser):
    AuthorizationRepository(database, current_user).require_project(project_id, Permission.MANAGE_PROJECTS)
    return CatalogRepository(database).archive_project(project_id)
