from hashlib import sha256

from s_usd_service.api.dependencies import get_object_storage


def create_version(client):
    project = client.post(
        "/api/v1/projects",
        json={"code": "ORB", "name": "Orbital Workshop"}
    ).json()
    asset = client.post(
        f"/api/v1/projects/{project['id']}/assets",
        json={"code": "rover", "name": "Survey Rover", "asset_type": "prop"}
    ).json()
    stream = client.post(
        f"/api/v1/assets/{asset['id']}/streams",
        json={"name": "model"}
    ).json()
    return client.post(
        f"/api/v1/streams/{stream['id']}/versions",
        json={"comment": "Initial model publish"}
    ).json()


def test_upload_list_metadata_download_and_delete(client):
    version = create_version(client)
    payload = b'#usda 1.0\n\ndef Xform "Rover"\n{\n}\n'

    upload = client.post(
        f"/api/v1/versions/{version['id']}/files",
        data={"role": "root_layer", "relative_path": "root/rover.usda"},
        files={"file": ("rover.usda", payload, "application/octet-stream")}
    )

    assert upload.status_code == 201
    uploaded = upload.json()
    assert uploaded["version_id"] == version["id"]
    assert uploaded["role"] == "root_layer"
    assert uploaded["relative_path"] == "root/rover.usda"
    assert uploaded["size_bytes"] == len(payload)
    assert uploaded["sha256"] == sha256(payload).hexdigest()
    assert uploaded["status"] == "available"

    version_response = client.get(f"/api/v1/versions/{version['id']}")
    assert version_response.json()["status"] == "uploaded"

    listing = client.get(f"/api/v1/versions/{version['id']}/files")
    assert listing.status_code == 200
    assert listing.json()["count"] == 1
    assert listing.json()["items"][0]["id"] == uploaded["id"]

    metadata = client.get(f"/api/v1/files/{uploaded['id']}")
    assert metadata.status_code == 200
    assert metadata.json()["content_url"].endswith(f"/{uploaded['id']}/content")

    download = client.get(f"/api/v1/files/{uploaded['id']}/content")
    assert download.status_code == 200
    assert download.content == payload
    assert download.headers["content-length"] == str(len(payload))
    assert download.headers["etag"] == f'"{sha256(payload).hexdigest()}"'
    assert "rover.usda" in download.headers["content-disposition"]

    deletion = client.delete(f"/api/v1/files/{uploaded['id']}")
    assert deletion.status_code == 200
    assert deletion.json()["object_existed"] is True
    assert client.get(f"/api/v1/files/{uploaded['id']}").status_code == 404


def test_duplicate_relative_path_returns_conflict_and_cleans_new_object(client):
    version = create_version(client)
    endpoint = f"/api/v1/versions/{version['id']}/files"
    upload = {
        "data": {"role": "root_layer", "relative_path": "root/rover.usda"},
        "files": {"file": ("rover.usda", b"first", "application/octet-stream")}
    }

    assert client.post(endpoint, **upload).status_code == 201
    duplicate = client.post(
        endpoint,
        data={"role": "root_layer", "relative_path": "root/rover.usda"},
        files={"file": ("rover_v2.usda", b"second", "application/octet-stream")}
    )

    assert duplicate.status_code == 409
    listing = client.get(endpoint).json()
    assert listing["count"] == 1
    assert len(list(get_object_storage().iter_keys())) == 1


def test_upload_rejects_relative_path_traversal(client):
    version = create_version(client)
    response = client.post(
        f"/api/v1/versions/{version['id']}/files",
        data={"role": "root_layer", "relative_path": "../outside.usda"},
        files={"file": ("outside.usda", b"bad", "application/octet-stream")}
    )

    assert response.status_code == 400
    assert list(get_object_storage().iter_keys()) == []


def test_download_marks_record_missing_when_object_disappears(client):
    version = create_version(client)
    upload = client.post(
        f"/api/v1/versions/{version['id']}/files",
        data={"relative_path": "root/rover.usda"},
        files={"file": ("rover.usda", b"content", "application/octet-stream")}
    ).json()
    storage = get_object_storage()
    storage.delete(upload["storage_key"])

    response = client.get(f"/api/v1/files/{upload['id']}/content")

    assert response.status_code == 404
    metadata = client.get(f"/api/v1/files/{upload['id']}").json()
    assert metadata["status"] == "missing"
