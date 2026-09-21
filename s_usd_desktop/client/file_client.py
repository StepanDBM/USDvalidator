import mimetypes
from pathlib import Path

from s_usd_desktop.client.models import StoredFileCollection, StoredFileRecord


class FileClient:
    def __init__(self, api):
        self.api = api

    def list_files(self, version_id):
        data = self.api.get(f"/api/v1/versions/{version_id}/files")
        return StoredFileCollection.from_dict(data)

    def get_file(self, file_id):
        return StoredFileRecord.from_dict(self.api.get(f"/api/v1/files/{file_id}"))

    def upload_file(self, version_id, source_path, role="other", relative_path=None):
        source_path = Path(source_path)

        with source_path.open("rb") as source:
            return self.upload_stream(
                version_id,
                source,
                source_path.name,
                role,
                relative_path or source_path.name
            )

    def upload_stream(self, version_id, source, filename, role="other", relative_path=None):
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        data = {"role": role, "relative_path": relative_path or filename}
        files = {"file": (filename, source, content_type)}
        result = self.api.post(f"/api/v1/versions/{version_id}/files", data=data, files=files)
        return StoredFileRecord.from_dict(result)

    def delete_file(self, file_id):
        return self.api.delete(f"/api/v1/files/{file_id}")
