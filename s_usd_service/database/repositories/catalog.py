from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from s_usd_service.database.models import Asset, Project, Stream, Version, WorkspaceMembership
from s_usd_service.database.repositories.errors import ConflictError, NotFoundError


class CatalogRepository:
    def __init__(self, database: Session):
        self.database = database

    def _commit(self, model, conflict_message):
        try:
            self.database.add(model)
            self.database.commit()
            self.database.refresh(model)
            return model
        except IntegrityError as error:
            self.database.rollback()
            raise ConflictError(conflict_message) from error

    def create_project(self, workspace_id: UUID, created_by_user_id: UUID, data):
        return self._commit(
            Project(workspace_id=workspace_id, created_by_user_id=created_by_user_id, **data),
            f"Project code '{data['code']}' already exists in workspace",
        )

    def list_projects(self, user_id: UUID, *, workspace_id=None, status=None, search=None, created_by_user_id=None):
        statement = (
            select(Project)
            .join(WorkspaceMembership, WorkspaceMembership.workspace_id == Project.workspace_id)
            .where(WorkspaceMembership.user_id == user_id)
        )
        if workspace_id is not None:
            statement = statement.where(Project.workspace_id == workspace_id)
        if status is not None:
            statement = statement.where(Project.status == status)
        if created_by_user_id is not None:
            statement = statement.where(Project.created_by_user_id == created_by_user_id)
        if search:
            pattern = f"%{search.strip()}%"
            statement = statement.where(
                or_(Project.code.ilike(pattern), Project.name.ilike(pattern), Project.description.ilike(pattern))
            )
        return list(self.database.scalars(statement.order_by(Project.code)).all())

    def update_project(self, project_id: UUID, data):
        project = self.get_project(project_id)
        for field, value in data.items():
            setattr(project, field, value)
        if "status" in data:
            project.archived_at = datetime.now(timezone.utc) if data["status"] == "archived" else None
        self.database.commit()
        self.database.refresh(project)
        return project

    def archive_project(self, project_id: UUID):
        return self.update_project(project_id, {"status": "archived"})

    def get_project(self, project_id: UUID):
        project = self.database.get(Project, project_id)
        if not project:
            raise NotFoundError("Project not found")
        return project

    def create_asset(self, project_id: UUID, data):
        project = self.get_project(project_id)
        if project.status == "archived":
            raise ConflictError("Archived projects cannot accept new assets")
        return self._commit(
            Asset(project_id=project_id, **data), f"Asset code '{data['code']}' already exists in project"
        )

    def list_assets(self, project_id: UUID):
        self.get_project(project_id)
        statement = select(Asset).where(Asset.project_id == project_id).order_by(Asset.code)
        return list(self.database.scalars(statement).all())

    def get_asset(self, asset_id: UUID):
        asset = self.database.get(Asset, asset_id)
        if not asset:
            raise NotFoundError("Asset not found")
        return asset

    def create_stream(self, asset_id: UUID, data):
        self.get_asset(asset_id)
        return self._commit(Stream(asset_id=asset_id, **data), f"Stream '{data['name']}' already exists for asset")

    def list_streams(self, asset_id: UUID):
        self.get_asset(asset_id)
        statement = select(Stream).where(Stream.asset_id == asset_id).order_by(Stream.name)
        return list(self.database.scalars(statement).all())

    def get_stream(self, stream_id: UUID):
        stream = self.database.get(Stream, stream_id)
        if not stream:
            raise NotFoundError("Stream not found")
        return stream

    def create_version(self, stream_id: UUID, data):
        self.get_stream(stream_id)
        latest = self.database.scalar(select(func.max(Version.number)).where(Version.stream_id == stream_id)) or 0
        return self._commit(
            Version(stream_id=stream_id, number=latest + 1, **data), "Version number conflict; retry request"
        )

    def list_versions(self, stream_id: UUID):
        self.get_stream(stream_id)
        statement = select(Version).where(Version.stream_id == stream_id).order_by(Version.number.desc())
        return list(self.database.scalars(statement).all())

    def get_version(self, version_id: UUID):
        version = self.database.get(Version, version_id)
        if not version:
            raise NotFoundError("Version not found")
        return version
