from s_usd_desktop.client.models import (
    AssetRecord,
    ProjectRecord,
    ServiceHealth,
    StreamRecord,
    VersionRecord
)


class CatalogClient:
    def __init__(self, api):
        self.api = api

    def get_health(self):
        return ServiceHealth.from_dict(self.api.get("/api/v1/health"))

    def list_projects(self):
        return tuple(ProjectRecord.from_dict(item) for item in self.api.get("/api/v1/projects"))

    def create_project(self, code, name, description=""):
        data = {"code": code, "name": name, "description": description}
        return ProjectRecord.from_dict(self.api.post("/api/v1/projects", json=data))

    def get_project(self, project_id):
        return ProjectRecord.from_dict(self.api.get(f"/api/v1/projects/{project_id}"))

    def list_assets(self, project_id):
        path = f"/api/v1/projects/{project_id}/assets"
        return tuple(AssetRecord.from_dict(item) for item in self.api.get(path))

    def create_asset(self, project_id, code, name, asset_type, description=""):
        path = f"/api/v1/projects/{project_id}/assets"
        data = {
            "code": code,
            "name": name,
            "asset_type": asset_type,
            "description": description
        }
        return AssetRecord.from_dict(self.api.post(path, json=data))

    def get_asset(self, asset_id):
        return AssetRecord.from_dict(self.api.get(f"/api/v1/assets/{asset_id}"))

    def list_streams(self, asset_id):
        path = f"/api/v1/assets/{asset_id}/streams"
        return tuple(StreamRecord.from_dict(item) for item in self.api.get(path))

    def create_stream(self, asset_id, name, description=""):
        path = f"/api/v1/assets/{asset_id}/streams"
        return StreamRecord.from_dict(self.api.post(path, json={"name": name, "description": description}))

    def get_stream(self, stream_id):
        return StreamRecord.from_dict(self.api.get(f"/api/v1/streams/{stream_id}"))

    def list_versions(self, stream_id):
        path = f"/api/v1/streams/{stream_id}/versions"
        return tuple(VersionRecord.from_dict(item) for item in self.api.get(path))

    def create_version(self, stream_id, comment=""):
        path = f"/api/v1/streams/{stream_id}/versions"
        return VersionRecord.from_dict(self.api.post(path, json={"comment": comment}))

    def get_version(self, version_id):
        return VersionRecord.from_dict(self.api.get(f"/api/v1/versions/{version_id}"))

    def publish_version(self, version_id):
        path = f"/api/v1/versions/{version_id}/publish"
        return VersionRecord.from_dict(self.api.post(path))

    def deprecate_version(self, version_id):
        path = f"/api/v1/versions/{version_id}/deprecate"
        return VersionRecord.from_dict(self.api.post(path))
