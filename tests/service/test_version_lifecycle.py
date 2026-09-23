from datetime import datetime, timedelta, timezone


def create_version(client):
    project = client.post(
        "/api/v1/projects",
        json={"code": "LIFE", "name": "Lifecycle"}
    ).json()
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
        json={"comment": "Lifecycle target"}
    ).json()


def upload(client, version_id, role="root_layer", path="root/probe.usda"):
    return client.post(
        f"/api/v1/versions/{version_id}/files",
        data={"role": role, "relative_path": path},
        files={"file": (path.rsplit("/", 1)[-1], b"#usda 1.0\n", "application/octet-stream")}
    )


def validation_payload(stored_file_id, passed=True, cancelled=False, schema="1.0.0"):
    started = datetime.now(timezone.utc)
    failed = 0 if passed else 1
    passed_count = 1 if passed else 0
    return {
        "stored_file_id": stored_file_id,
        "profile_name": "production/default",
        "report_schema_version": schema,
        "tool_name": "S-USDv",
        "tool_version": "0.9.0",
        "configuration_fingerprint": "a" * 64,
        "check_catalog_fingerprint": "b" * 64,
        "started_at": started.isoformat(),
        "completed_at": (started + timedelta(seconds=1)).isoformat(),
        "duration_seconds": 1.0,
        "publish_passed": passed,
        "summary": {
            "total": 1,
            "passed": passed_count,
            "failed": failed,
            "skipped": 0,
            "errors": 0,
            "warnings": 0
        },
        "report": {
            "schema": {"name": "s-usdv.validation_report", "version": schema},
            "validation": {"cancelled": cancelled},
            "results": []
        }
    }


def get_version(client, version_id):
    response = client.get(f"/api/v1/versions/{version_id}")
    assert response.status_code == 200
    return response.json()


def test_root_upload_and_validation_drive_lifecycle(client):
    version = create_version(client)
    assert version["status"] == "draft"

    dependency = upload(client, version["id"], "dependency", "layers/geo.usda")
    assert dependency.status_code == 201
    assert get_version(client, version["id"])["status"] == "draft"

    root = upload(client, version["id"]).json()
    assert get_version(client, version["id"])["status"] == "uploaded"

    failed = client.post(
        f"/api/v1/versions/{version['id']}/validation-runs",
        json=validation_payload(root["id"], passed=False)
    )
    assert failed.status_code == 201
    assert get_version(client, version["id"])["status"] == "validation_failed"

    passed = client.post(
        f"/api/v1/versions/{version['id']}/validation-runs",
        json=validation_payload(root["id"], passed=True)
    )
    assert passed.status_code == 201
    assert get_version(client, version["id"])["status"] == "validated"


def test_publish_requires_latest_passing_root_validation(client):
    version = create_version(client)
    root = upload(client, version["id"]).json()

    no_validation = client.post(f"/api/v1/versions/{version['id']}/publish")
    assert no_validation.status_code == 409

    client.post(
        f"/api/v1/versions/{version['id']}/validation-runs",
        json=validation_payload(root["id"], passed=True)
    )
    published = client.post(f"/api/v1/versions/{version['id']}/publish")

    assert published.status_code == 200
    assert published.json()["status"] == "published"


def test_latest_failed_validation_blocks_publish(client):
    version = create_version(client)
    root = upload(client, version["id"]).json()
    endpoint = f"/api/v1/versions/{version['id']}/validation-runs"
    assert client.post(endpoint, json=validation_payload(root["id"], passed=True)).status_code == 201
    assert client.post(endpoint, json=validation_payload(root["id"], passed=False)).status_code == 201

    response = client.post(f"/api/v1/versions/{version['id']}/publish")

    assert response.status_code == 409
    assert "did not pass" in response.json()["detail"]


def test_publish_rejects_cancelled_and_unsupported_reports(client):
    version = create_version(client)
    root = upload(client, version["id"]).json()
    endpoint = f"/api/v1/versions/{version['id']}/validation-runs"
    client.post(endpoint, json=validation_payload(root["id"], passed=True, cancelled=True))
    assert client.post(f"/api/v1/versions/{version['id']}/publish").status_code == 409

    client.post(endpoint, json=validation_payload(root["id"], passed=True, schema="9.9.9"))
    unsupported = client.post(f"/api/v1/versions/{version['id']}/publish")
    assert unsupported.status_code == 409
    assert "Unsupported" in unsupported.json()["detail"]


def test_only_published_versions_can_be_deprecated(client):
    version = create_version(client)
    assert client.post(f"/api/v1/versions/{version['id']}/deprecate").status_code == 409
    root = upload(client, version["id"]).json()
    client.post(
        f"/api/v1/versions/{version['id']}/validation-runs",
        json=validation_payload(root["id"], passed=True)
    )
    client.post(f"/api/v1/versions/{version['id']}/publish")

    deprecated = client.post(f"/api/v1/versions/{version['id']}/deprecate")

    assert deprecated.status_code == 200
    assert deprecated.json()["status"] == "deprecated"


def publish_version(client, version_id):
    root = upload(client, version_id).json()
    client.post(
        f"/api/v1/versions/{version_id}/validation-runs",
        json=validation_payload(root["id"], passed=True)
    )
    response = client.post(f"/api/v1/versions/{version_id}/publish")
    assert response.status_code == 200
    return root


def test_published_version_rejects_upload_and_delete(client):
    version = create_version(client)
    root = publish_version(client, version["id"])

    added = upload(client, version["id"], "dependency", "layers/late.usda")
    deleted = client.delete(f"/api/v1/files/{root['id']}")

    assert added.status_code == 409
    assert "immutable" in added.json()["detail"]
    assert deleted.status_code == 409
    assert "immutable" in deleted.json()["detail"]
    listing = client.get(f"/api/v1/versions/{version['id']}/files").json()
    assert listing["count"] == 1
    assert get_version(client, version["id"])["status"] == "published"


def test_deprecated_version_remains_immutable(client):
    version = create_version(client)
    root = publish_version(client, version["id"])
    client.post(f"/api/v1/versions/{version['id']}/deprecate")

    added = upload(client, version["id"], "dependency", "layers/late.usda")
    deleted = client.delete(f"/api/v1/files/{root['id']}")

    assert added.status_code == 409
    assert deleted.status_code == 409
    assert get_version(client, version["id"])["status"] == "deprecated"


def test_dependency_mutation_invalidates_validation_status(client):
    version = create_version(client)
    root = upload(client, version["id"]).json()
    dependency = upload(
        client,
        version["id"],
        "dependency",
        "layers/geo.usda"
    ).json()
    client.post(
        f"/api/v1/versions/{version['id']}/validation-runs",
        json=validation_payload(root["id"], passed=True)
    )
    assert get_version(client, version["id"])["status"] == "validated"

    added = upload(client, version["id"], "dependency", "layers/look.usda")
    assert added.status_code == 201
    assert get_version(client, version["id"])["status"] == "uploaded"

    client.post(
        f"/api/v1/versions/{version['id']}/validation-runs",
        json=validation_payload(root["id"], passed=True)
    )
    assert get_version(client, version["id"])["status"] == "validated"

    deleted = client.delete(f"/api/v1/files/{dependency['id']}")
    assert deleted.status_code == 200
    assert get_version(client, version["id"])["status"] == "uploaded"


def test_deleting_root_returns_version_to_draft(client):
    version = create_version(client)
    root = upload(client, version["id"]).json()
    client.post(
        f"/api/v1/versions/{version['id']}/validation-runs",
        json=validation_payload(root["id"], passed=True)
    )
    assert get_version(client, version["id"])["status"] == "validated"

    response = client.delete(f"/api/v1/files/{root['id']}")

    assert response.status_code == 200
    assert get_version(client, version["id"])["status"] == "draft"
