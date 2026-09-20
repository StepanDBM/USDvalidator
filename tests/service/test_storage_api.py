from io import BytesIO
from uuid import uuid4

from s_usd_service.api.dependencies import get_object_storage
from s_usd_service.database.models import Asset, Project, StoredFile, Stream, Version
from s_usd_service.database.session import SessionLocal


def seed_api_file(storage):
    with SessionLocal() as database:
        project = Project(code=f"P{uuid4().hex[:8]}", name="Nebula")
        asset = Asset(project=project, code="satellite", name="Satellite", asset_type="prop")
        stream = Stream(asset=asset, name="model")
        version = Version(stream=stream, number=1, status="uploaded")
        key = f"projects/NEBULA/assets/satellite/{uuid4().hex}/root.usda"
        result = storage.write_stream(BytesIO(b"#usda 1.0\n"), key)
        stored_file = StoredFile(
            version=version,
            role="root_layer",
            original_name="root.usda",
            relative_path="root.usda",
            storage_key=key,
            content_type="application/octet-stream",
            size_bytes=result.size_bytes,
            sha256=result.sha256,
            status="available"
        )
        database.add(stored_file)
        database.commit()
        database.refresh(stored_file)
        return stored_file.id, key


def test_delete_file_endpoint(client):
    storage = get_object_storage()
    file_id, key = seed_api_file(storage)

    response = client.delete(f"/api/v1/files/{file_id}")

    assert response.status_code == 200
    assert response.json()["metadata_deleted"] is True
    assert storage.exists(key) is False


def test_reconciliation_endpoint_detects_orphan(client):
    storage = get_object_storage()
    key = f"projects/NEBULA/orphan/{uuid4().hex}.usda"
    storage.write_stream(BytesIO(b"orphan"), key)

    response = client.post("/api/v1/storage/reconcile")

    assert response.status_code == 200
    assert key in response.json()["orphaned_storage_objects"]

    repaired = client.post("/api/v1/storage/reconcile?delete_orphans=true")
    assert repaired.status_code == 200
    assert key in repaired.json()["deleted_orphaned_objects"]
    assert storage.exists(key) is False
