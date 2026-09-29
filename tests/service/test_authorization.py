PASSWORD = "correct horse battery staple"


def create_user(client, email):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "display_name": email.split("@")[0], "password": PASSWORD},
    )
    assert response.status_code == 201


def login(client, email):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_workspace(client, headers, code):
    response = client.post("/api/v1/workspaces", headers=headers, json={"code": code, "name": f"{code} Workspace"})
    assert response.status_code == 201
    return response.json()


def add_member(client, headers, workspace_id, email, role):
    response = client.post(
        f"/api/v1/workspaces/{workspace_id}/members",
        headers=headers,
        json={"email": email, "role": role},
    )
    assert response.status_code == 201
    return response.json()


def create_project(client, headers, workspace_id, code="PRJ"):
    return client.post(
        "/api/v1/projects",
        headers=headers,
        json={"workspace_id": workspace_id, "code": code, "name": code},
    )


def test_protected_catalog_requires_authentication(anonymous_client):
    assert anonymous_client.get("/api/v1/projects").status_code == 401
    assert anonymous_client.get("/api/v1/workspaces").status_code == 401
    assert anonymous_client.get("/api/v1/health").status_code == 200


def test_workspace_creator_is_owner_and_can_list_members(anonymous_client):
    create_user(anonymous_client, "owner@example.com")
    owner_headers = login(anonymous_client, "owner@example.com")
    workspace = create_workspace(anonymous_client, owner_headers, "OWN")
    memberships = anonymous_client.get(f"/api/v1/workspaces/{workspace['id']}/members", headers=owner_headers)
    assert memberships.status_code == 200
    assert len(memberships.json()) == 1
    assert memberships.json()[0]["role"] == "owner"


def test_viewer_can_read_but_cannot_create_catalog_content(anonymous_client):
    for email in ("owner@example.com", "viewer@example.com"):
        create_user(anonymous_client, email)
    owner_headers = login(anonymous_client, "owner@example.com")
    viewer_headers = login(anonymous_client, "viewer@example.com")
    workspace = create_workspace(anonymous_client, owner_headers, "VIEW")
    add_member(anonymous_client, owner_headers, workspace["id"], "viewer@example.com", "viewer")
    project = create_project(anonymous_client, owner_headers, workspace["id"]).json()

    assert anonymous_client.get(f"/api/v1/projects/{project['id']}", headers=viewer_headers).status_code == 200
    denied = anonymous_client.post(
        f"/api/v1/projects/{project['id']}/assets",
        headers=viewer_headers,
        json={"code": "hero", "name": "Hero", "asset_type": "character"},
    )
    assert denied.status_code == 403


def test_contributor_can_create_assets_but_cannot_create_projects(anonymous_client):
    for email in ("owner@example.com", "artist@example.com"):
        create_user(anonymous_client, email)
    owner_headers = login(anonymous_client, "owner@example.com")
    artist_headers = login(anonymous_client, "artist@example.com")
    workspace = create_workspace(anonymous_client, owner_headers, "CONT")
    add_member(anonymous_client, owner_headers, workspace["id"], "artist@example.com", "contributor")
    project = create_project(anonymous_client, owner_headers, workspace["id"]).json()

    asset = anonymous_client.post(
        f"/api/v1/projects/{project['id']}/assets",
        headers=artist_headers,
        json={"code": "hero", "name": "Hero", "asset_type": "character"},
    )
    assert asset.status_code == 201
    assert create_project(anonymous_client, artist_headers, workspace["id"], "NOPE").status_code == 403


def test_administrator_manages_regular_members_but_not_administrators(anonymous_client):
    emails = ("owner@example.com", "admin@example.com", "viewer@example.com", "other-admin@example.com")
    for email in emails:
        create_user(anonymous_client, email)
    owner_headers = login(anonymous_client, "owner@example.com")
    admin_headers = login(anonymous_client, "admin@example.com")
    workspace = create_workspace(anonymous_client, owner_headers, "ADMIN")
    add_member(anonymous_client, owner_headers, workspace["id"], "admin@example.com", "administrator")

    assert (
        add_member(anonymous_client, admin_headers, workspace["id"], "viewer@example.com", "viewer")["role"] == "viewer"
    )
    denied = anonymous_client.post(
        f"/api/v1/workspaces/{workspace['id']}/members",
        headers=admin_headers,
        json={"email": "other-admin@example.com", "role": "administrator"},
    )
    assert denied.status_code == 403


def test_final_owner_cannot_be_demoted_or_removed(anonymous_client):
    create_user(anonymous_client, "owner@example.com")
    owner_headers = login(anonymous_client, "owner@example.com")
    workspace = create_workspace(anonymous_client, owner_headers, "FINAL")
    membership = anonymous_client.get(f"/api/v1/workspaces/{workspace['id']}/members", headers=owner_headers).json()[0]

    demote = anonymous_client.patch(
        f"/api/v1/workspaces/{workspace['id']}/members/{membership['id']}",
        headers=owner_headers,
        json={"role": "administrator"},
    )
    remove = anonymous_client.delete(
        f"/api/v1/workspaces/{workspace['id']}/members/{membership['id']}", headers=owner_headers
    )
    assert demote.status_code == 409
    assert remove.status_code == 409


def test_cross_workspace_resources_are_not_disclosed(anonymous_client):
    for email in ("alpha@example.com", "beta@example.com"):
        create_user(anonymous_client, email)
    alpha_headers = login(anonymous_client, "alpha@example.com")
    beta_headers = login(anonymous_client, "beta@example.com")
    alpha = create_workspace(anonymous_client, alpha_headers, "ALPHA")
    create_workspace(anonymous_client, beta_headers, "BETA")
    project = create_project(anonymous_client, alpha_headers, alpha["id"]).json()

    assert anonymous_client.get(f"/api/v1/projects/{project['id']}", headers=beta_headers).status_code == 404
    assert project["id"] not in {
        item["id"] for item in anonymous_client.get("/api/v1/projects", headers=beta_headers).json()
    }


def test_project_codes_are_unique_per_workspace(anonymous_client):
    create_user(anonymous_client, "owner@example.com")
    headers = login(anonymous_client, "owner@example.com")
    first = create_workspace(anonymous_client, headers, "FIRST")
    second = create_workspace(anonymous_client, headers, "SECOND")
    assert create_project(anonymous_client, headers, first["id"], "SAME").status_code == 201
    assert create_project(anonymous_client, headers, second["id"], "SAME").status_code == 201
    assert create_project(anonymous_client, headers, first["id"], "SAME").status_code == 409


def test_global_storage_reconciliation_requires_platform_admin(anonymous_client):
    create_user(anonymous_client, "owner@example.com")
    headers = login(anonymous_client, "owner@example.com")
    create_workspace(anonymous_client, headers, "STORE")
    response = anonymous_client.post("/api/v1/storage/reconcile", headers=headers)
    assert response.status_code == 403
