import json
from uuid import UUID

import httpx

from s_usd_desktop.client import ApiClientConfiguration, CatalogClient, SUsdvApiClient

PROJECT_ID = "11111111-1111-4111-8111-111111111111"
ASSET_ID = "22222222-2222-4222-8222-222222222222"
STREAM_ID = "33333333-3333-4333-8333-333333333333"
VERSION_ID = "44444444-4444-4444-8444-444444444444"
DATE = "2026-09-21T10:00:00+00:00"


def handler(request):
    responses = {
        ("GET", "/api/v1/health"): {"status": "healthy", "service": "S-USDv Service", "version": "0.3.0"},
        ("GET", "/api/v1/projects"): [{
            "id": PROJECT_ID,
            "code": "ORB",
            "name": "Orbital Workshop",
            "description": "",
            "status": "active",
            "created_at": DATE,
            "updated_at": DATE
        }],
        ("GET", f"/api/v1/projects/{PROJECT_ID}/assets"): [{
            "id": ASSET_ID,
            "project_id": PROJECT_ID,
            "code": "rover",
            "name": "Survey Rover",
            "asset_type": "prop",
            "description": "",
            "status": "active",
            "created_at": DATE,
            "updated_at": DATE
        }],
        ("GET", f"/api/v1/assets/{ASSET_ID}/streams"): [{
            "id": STREAM_ID,
            "asset_id": ASSET_ID,
            "name": "model",
            "description": "",
            "created_at": DATE,
            "updated_at": DATE
        }],
        ("GET", f"/api/v1/streams/{STREAM_ID}/versions"): [{
            "id": VERSION_ID,
            "stream_id": STREAM_ID,
            "number": 7,
            "status": "uploaded",
            "comment": "Model update",
            "created_at": DATE,
            "updated_at": DATE
        }]
    }
    return httpx.Response(200, json=responses[(request.method, request.url.path)])


def test_parses_catalog_hierarchy():
    with SUsdvApiClient(ApiClientConfiguration(), transport=httpx.MockTransport(handler)) as api:
        catalog = CatalogClient(api)
        health = catalog.get_health()
        projects = catalog.list_projects()
        assets = catalog.list_assets(PROJECT_ID)
        streams = catalog.list_streams(ASSET_ID)
        versions = catalog.list_versions(STREAM_ID)

    assert health.service == "S-USDv Service"
    assert projects[0].id == UUID(PROJECT_ID)
    assert assets[0].project_id == UUID(PROJECT_ID)
    assert streams[0].asset_id == UUID(ASSET_ID)
    assert versions[0].display_name == "v0007"


def test_create_project_sends_expected_payload():
    captured = {}

    def create_handler(request):
        captured["payload"] = json.loads(request.content)
        return httpx.Response(201, json={
            "id": PROJECT_ID,
            "code": "LUM",
            "name": "Lumen",
            "description": "Lighting tests",
            "status": "active",
            "created_at": DATE,
            "updated_at": DATE
        })

    with SUsdvApiClient(transport=httpx.MockTransport(create_handler)) as api:
        project = CatalogClient(api).create_project("LUM", "Lumen", "Lighting tests")

    assert captured["payload"] == {
        "code": "LUM",
        "name": "Lumen",
        "description": "Lighting tests"
    }
    assert project.code == "LUM"



def test_publish_and_deprecate_version_use_transition_endpoints():
    captured = []

    def transition_handler(request):
        captured.append((request.method, request.url.path))
        status = "published" if request.url.path.endswith("/publish") else "deprecated"
        return httpx.Response(200, json={
            "id": VERSION_ID,
            "stream_id": STREAM_ID,
            "number": 2,
            "status": status,
            "comment": "Ready",
            "created_at": DATE,
            "updated_at": DATE
        })

    with SUsdvApiClient(transport=httpx.MockTransport(transition_handler)) as api:
        catalog = CatalogClient(api)
        published = catalog.publish_version(VERSION_ID)
        deprecated = catalog.deprecate_version(VERSION_ID)

    assert published.status == "published"
    assert deprecated.status == "deprecated"
    assert captured == [
        ("POST", f"/api/v1/versions/{VERSION_ID}/publish"),
        ("POST", f"/api/v1/versions/{VERSION_ID}/deprecate")
    ]
