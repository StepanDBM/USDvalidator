from io import BytesIO

import pytest

from s_usd_service.api.dependencies import get_object_storage
from s_usd_service.config import get_settings
from s_usd_service.database.repositories.catalog import CatalogRepository
from s_usd_service.database.session import SessionLocal
from s_usd_service.services.file_transfer import FileTransferService
from s_usd_service.storage.errors import StorageLimitExceededError
from s_usd_service.storage.local import LocalObjectStorage


def create_version(database):
    catalog = CatalogRepository(database)
    project = catalog.create_project({"code": "LUM", "name": "Lumen", "description": ""})
    asset = catalog.create_asset(project.id, {
        "code": "probe",
        "name": "Light Probe",
        "asset_type": "prop",
        "description": ""
    })
    stream = catalog.create_stream(asset.id, {"name": "model", "description": ""})
    return catalog.create_version(stream.id, {"comment": "Hardening test"})


def upload(client, version_id, filename, payload, role="other", relative_path=None):
    return client.post(
        f"/api/v1/versions/{version_id}/files",
        data={"role": role, "relative_path": relative_path or filename},
        files={"file": (filename, payload, "application/octet-stream")}
    )


def test_rejects_empty_upload_and_leaves_no_object(client):
    with SessionLocal() as database:
        version = create_version(database)
        version_id = version.id

    response = upload(client, version_id, "empty.usda", b"", "root_layer")

    assert response.status_code == 400
    assert response.json()["detail"] == "Empty files cannot be uploaded"
    assert list(get_object_storage().iter_keys()) == []


def test_rejects_non_usd_extension(client):
    with SessionLocal() as database:
        version = create_version(database)
        version_id = version.id

    response = upload(client, version_id, "notes.txt", b"text", relative_path="notes.txt")

    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()["detail"]


def test_rejects_invalid_role(client):
    with SessionLocal() as database:
        version = create_version(database)
        version_id = version.id

    response = upload(client, version_id, "probe.usda", b"#usda 1.0\n", role="mystery")

    assert response.status_code == 400
    assert "Unsupported file role" in response.json()["detail"]


def test_allows_only_one_root_layer_per_version(client):
    with SessionLocal() as database:
        version = create_version(database)
        version_id = version.id

    first = upload(client, version_id, "root.usda", b"#usda 1.0\n", "root_layer")
    second = upload(
        client,
        version_id,
        "second.usda",
        b"#usda 1.0\n",
        "root_layer",
        "root/second.usda"
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_storage_limit_cleans_partial_file(tmp_path):
    storage = LocalObjectStorage(tmp_path / "storage", tmp_path / "temp", chunk_size=4)

    with pytest.raises(StorageLimitExceededError):
        storage.write_stream(BytesIO(b"123456789"), "objects/large.usda", maximum_bytes=8)

    assert storage.exists("objects/large.usda") is False
    assert list((tmp_path / "temp").glob("*.part")) == []


def test_complete_milestone_flow(client):
    project = client.post(
        "/api/v1/projects",
        json={"code": "AST", "name": "Asteroid Lab"}
    ).json()
    asset = client.post(
        f"/api/v1/projects/{project['id']}/assets",
        json={"code": "drone", "name": "Mining Drone", "asset_type": "prop"}
    ).json()
    stream = client.post(
        f"/api/v1/assets/{asset['id']}/streams",
        json={"name": "model"}
    ).json()
    version = client.post(
        f"/api/v1/streams/{stream['id']}/versions",
        json={"comment": "Milestone integration"}
    ).json()
    payload = b'#usda 1.0\n\ndef Xform "MiningDrone"\n{\n}\n'
    uploaded = upload(
        client,
        version["id"],
        "drone.usda",
        payload,
        "root_layer",
        "root/drone.usda"
    ).json()

    assert client.get(f"/api/v1/files/{uploaded['id']}/content").content == payload
    assert client.delete(f"/api/v1/files/{uploaded['id']}").status_code == 200
    reconciliation = client.post("/api/v1/storage/reconcile").json()
    assert reconciliation["consistent_before"] is True
    assert reconciliation["consistent_after"] is True
