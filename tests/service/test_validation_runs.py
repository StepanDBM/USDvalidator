from datetime import datetime, timedelta, timezone


def create_version(client):
    project = client.post("/api/v1/projects", json={"code": "VAL", "name": "Validation"}).json()
    asset = client.post(
        f"/api/v1/projects/{project['id']}/assets",
        json={"code": "probe", "name": "Probe", "asset_type": "prop"}
    ).json()
    stream = client.post(
        f"/api/v1/assets/{asset['id']}/streams",
        json={"name": "model"}
    ).json()
    return client.post(
        f"/api/v1/streams/{stream['id']}/versions",
        json={"comment": "Validation target"}
    ).json()


def payload():
    started = datetime.now(timezone.utc)
    return {
        "profile_name": "production/default",
        "report_schema_version": "1.0.0",
        "tool_name": "S-USDv",
        "tool_version": "0.5.0",
        "configuration_fingerprint": "a" * 64,
        "check_catalog_fingerprint": "b" * 64,
        "started_at": started.isoformat(),
        "completed_at": (started + timedelta(seconds=1.25)).isoformat(),
        "duration_seconds": 1.25,
        "publish_passed": False,
        "summary": {
            "total": 4,
            "passed": 2,
            "failed": 1,
            "skipped": 0,
            "errors": 1,
            "warnings": 1
        },
        "report": {
            "schema": {"name": "s-usdv.validation", "version": "1.0.0"},
            "results": [{"check_id": "USD_STAGE_CAN_OPEN", "status": "PASSED"}]
        }
    }


def test_create_list_and_get_validation_run(client):
    version = create_version(client)
    response = client.post(
        f"/api/v1/versions/{version['id']}/validation-runs",
        json=payload()
    )
    assert response.status_code == 201
    created = response.json()
    assert created["version_id"] == version["id"]
    assert created["profile_name"] == "production/default"
    assert created["total_count"] == 4
    assert created["failed_count"] == 1
    assert created["report"]["results"][0]["check_id"] == "USD_STAGE_CAN_OPEN"

    listed = client.get(
        f"/api/v1/versions/{version['id']}/validation-runs"
    )
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert "report" not in listed.json()[0]

    detail = client.get(f"/api/v1/validation-runs/{created['id']}")
    assert detail.status_code == 200
    assert detail.json()["report"] == created["report"]


def test_rejects_validation_run_for_missing_version(client):
    response = client.post(
        "/api/v1/versions/00000000-0000-0000-0000-000000000000/validation-runs",
        json=payload()
    )
    assert response.status_code == 404


def test_rejects_invalid_summary_and_times(client):
    version = create_version(client)
    data = payload()
    data["summary"]["passed"] = 99
    response = client.post(
        f"/api/v1/versions/{version['id']}/validation-runs",
        json=data
    )
    assert response.status_code == 422

    data = payload()
    data["completed_at"] = "2020-01-01T00:00:00Z"
    response = client.post(
        f"/api/v1/versions/{version['id']}/validation-runs",
        json=data
    )
    assert response.status_code == 422
