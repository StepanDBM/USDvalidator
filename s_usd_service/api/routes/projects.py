from uuid import UUID

from fastapi import APIRouter, status

from s_usd_service.api.dependencies import DatabaseSession
from s_usd_service.api.schemas.catalog import ProjectCreate, ProjectRead
from s_usd_service.database.repositories.catalog import CatalogRepository

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, database: DatabaseSession):
    return CatalogRepository(database).create_project(payload.model_dump())


@router.get("", response_model=list[ProjectRead])
def list_projects(database: DatabaseSession):
    return CatalogRepository(database).list_projects()


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: UUID, database: DatabaseSession):
    return CatalogRepository(database).get_project(project_id)
