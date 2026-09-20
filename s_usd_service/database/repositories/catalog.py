from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from s_usd_service.database.models import Asset, Project, Stream, Version
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

    def create_project(self, data):
        return self._commit(Project(**data), f"Project code '{data['code']}' already exists")

    def list_projects(self):
        return list(self.database.scalars(select(Project).order_by(Project.code)).all())

    def get_project(self, project_id: UUID):
        project = self.database.get(Project, project_id)
        if not project:
            raise NotFoundError("Project not found")
        return project

    def create_asset(self, project_id: UUID, data):
        self.get_project(project_id)
        return self._commit(Asset(project_id=project_id, **data), f"Asset code '{data['code']}' already exists in project")

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
        return self._commit(Version(stream_id=stream_id, number=latest + 1, **data), "Version number conflict; retry request")

    def list_versions(self, stream_id: UUID):
        self.get_stream(stream_id)
        statement = select(Version).where(Version.stream_id == stream_id).order_by(Version.number.desc())
        return list(self.database.scalars(statement).all())

    def get_version(self, version_id: UUID):
        version = self.database.get(Version, version_id)
        if not version:
            raise NotFoundError("Version not found")
        return version
