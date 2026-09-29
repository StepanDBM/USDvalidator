from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from s_usd_service.api.dependencies import CurrentUser, DatabaseSession
from s_usd_service.api.schemas.catalog import ProjectCreate, ProjectRead
from s_usd_service.database.repositories.authorization import AuthorizationRepository
from s_usd_service.database.repositories.catalog import CatalogRepository
from s_usd_service.domain.authorization import Permission

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
def list_projects(database: DatabaseSession, current_user: CurrentUser):
    return CatalogRepository(database).list_projects(current_user.id)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: UUID, database: DatabaseSession, current_user: CurrentUser):
    AuthorizationRepository(database, current_user).require_project(project_id)
    return CatalogRepository(database).get_project(project_id)
