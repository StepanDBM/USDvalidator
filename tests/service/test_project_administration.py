from uuid import uuid4


def create_project(client, code, name, profile="default"):
    return client.post(
        "/api/v1/projects",
        json={
            "workspace_id": client.workspace_id,
            "code": code,
            "name": name,
            "description": f"{name} production",
            "default_validation_profile": profile,
        },
    )


def test_project_provenance_profile_and_updates(client):
    created = create_project(client, "ADMIN", "Administration", "asset-strict")
    assert created.status_code == 201
    project = created.json()
    assert project["workspace_id"] == client.workspace_id
    assert project["created_by_user_id"]
    assert project["default_validation_profile"] == "asset-strict"
    assert project["status"] == "active"

    updated = client.patch(
        f"/api/v1/projects/{project['id']}",
        json={"name": "Administration Updated", "status": "on_hold", "default_validation_profile": "review"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Administration Updated"
    assert updated.json()["status"] == "on_hold"
    assert updated.json()["default_validation_profile"] == "review"


def test_project_filters_are_workspace_scoped(client):
    first = create_project(client, "ALPHA", "Alpha Lighting").json()
    create_project(client, "BETA", "Beta Modeling")

    by_workspace = client.get(f"/api/v1/projects?workspace_id={client.workspace_id}")
    assert by_workspace.status_code == 200
    assert {item["code"] for item in by_workspace.json()} >= {"ALPHA", "BETA"}

    searched = client.get("/api/v1/projects?search=lighting")
    assert searched.status_code == 200
    assert [item["id"] for item in searched.json()] == [first["id"]]

    by_creator = client.get(f"/api/v1/projects?created_by_user_id={first['created_by_user_id']}")
    assert by_creator.status_code == 200
    assert {item["code"] for item in by_creator.json()} >= {"ALPHA", "BETA"}


def test_archive_preserves_history_and_blocks_new_assets(client):
    project = create_project(client, "ARCHIVE", "Archive Me").json()
    asset = client.post(
        f"/api/v1/projects/{project['id']}/assets",
        json={"code": "existing", "name": "Existing", "asset_type": "prop", "description": ""},
    )
    assert asset.status_code == 201

    archived = client.post(f"/api/v1/projects/{project['id']}/archive")
    assert archived.status_code == 200
    assert archived.json()["status"] == "archived"
    assert archived.json()["archived_at"]

    history = client.get(f"/api/v1/projects/{project['id']}/assets")
    assert history.status_code == 200
    assert [item["id"] for item in history.json()] == [asset.json()["id"]]

    rejected = client.post(
        f"/api/v1/projects/{project['id']}/assets",
        json={"code": "new", "name": "New", "asset_type": "prop", "description": ""},
    )
    assert rejected.status_code == 409

    filtered = client.get("/api/v1/projects?status=archived")
    assert filtered.status_code == 200
    assert project["id"] in {item["id"] for item in filtered.json()}


def test_invalid_filter_and_cross_workspace_filter_are_rejected(client):
    assert client.get("/api/v1/projects?status=deleted").status_code == 422
    assert client.get(f"/api/v1/projects?workspace_id={uuid4()}").status_code == 404
