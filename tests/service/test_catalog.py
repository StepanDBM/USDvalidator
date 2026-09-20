def test_vertical_catalog_flow(client):
    project = client.post("/api/v1/projects", json={"code": "kan", "name": "Kaneda"})
    assert project.status_code == 201
    project_data = project.json()
    assert project_data["code"] == "KAN"

    asset = client.post(f"/api/v1/projects/{project_data['id']}/assets", json={"code": "Hero", "name": "Hero Character", "asset_type": "character"})
    assert asset.status_code == 201
    asset_data = asset.json()
    assert asset_data["code"] == "hero"

    stream = client.post(f"/api/v1/assets/{asset_data['id']}/streams", json={"name": "Rig"})
    assert stream.status_code == 201
    stream_data = stream.json()
    assert stream_data["name"] == "rig"

    first = client.post(f"/api/v1/streams/{stream_data['id']}/versions", json={"comment": "Initial rig publish"})
    second = client.post(f"/api/v1/streams/{stream_data['id']}/versions", json={"comment": "Shoulder update"})
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["number"] == 1
    assert second.json()["number"] == 2

    versions = client.get(f"/api/v1/streams/{stream_data['id']}/versions")
    assert versions.status_code == 200
    assert [item["number"] for item in versions.json()] == [2, 1]


def test_duplicate_project_returns_conflict(client):
    payload = {"code": "KAN", "name": "Kaneda"}
    assert client.post("/api/v1/projects", json=payload).status_code == 201
    response = client.post("/api/v1/projects", json=payload)
    assert response.status_code == 409
