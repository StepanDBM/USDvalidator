import json
from uuid import uuid4

import httpx

from s_usd_desktop.client.api_client import SUsdvApiClient
from s_usd_desktop.client.catalog_client import CatalogClient

DATE = "2026-09-29T20:00:00+00:00"
PROJECT_ID = str(uuid4())
WORKSPACE_ID = str(uuid4())
USER_ID = str(uuid4())


def payload(**changes):
    value = {
        "id": PROJECT_ID,
        "workspace_id": WORKSPACE_ID,
        "created_by_user_id": USER_ID,
        "code": "SHIP",
        "name": "Ship",
        "description": "Project",
        "status": "active",
        "default_validation_profile": "asset-strict",
        "archived_at": None,
        "created_at": DATE,
        "updated_at": DATE,
    }
    value.update(changes)
    return value


def test_project_client_sends_filters_and_profile():
    captured = []

    def handler(request):
        captured.append(request)
        if request.method == "GET":
            return httpx.Response(200, json=[payload()])
        return httpx.Response(201, json=payload())

    with SUsdvApiClient(transport=httpx.MockTransport(handler)) as api:
        client = CatalogClient(api)
        records = client.list_projects(workspace_id=WORKSPACE_ID, status="active", search="ship")
        created = client.create_project("SHIP", "Ship", "Project", "asset-strict")

    assert records[0].default_validation_profile == "asset-strict"
    assert dict(captured[0].url.params) == {"workspace_id": WORKSPACE_ID, "status": "active", "search": "ship"}
    assert json.loads(captured[1].content)["default_validation_profile"] == "asset-strict"
    assert created.created_by_user_id


def test_project_client_updates_and_archives():
    captured = []

    def handler(request):
        captured.append((request.method, request.url.path, json.loads(request.content) if request.content else None))
        return httpx.Response(200, json=payload(status="archived", archived_at=DATE))

    with SUsdvApiClient(transport=httpx.MockTransport(handler)) as api:
        client = CatalogClient(api)
        client.update_project(PROJECT_ID, status="on_hold", default_validation_profile="review")
        archived = client.archive_project(PROJECT_ID)

    assert captured[0] == (
        "PATCH",
        f"/api/v1/projects/{PROJECT_ID}",
        {"status": "on_hold", "default_validation_profile": "review"},
    )
    assert captured[1] == ("POST", f"/api/v1/projects/{PROJECT_ID}/archive", None)
    assert archived.status == "archived"
    assert archived.archived_at is not None
