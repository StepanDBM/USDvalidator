from io import BytesIO
from uuid import uuid4

from sqlalchemy import select

from s_usd_service.api.dependencies import get_object_storage
from s_usd_service.database.models import (
    Asset,
    Project,
    StoredFile,
    Stream,
    ValidationJob,
    Version,
    WorkspaceMembership,
)
from s_usd_service.database.session import SessionLocal
from s_usd_service.services.validation_job_worker import ValidationJobWorker


def seed_version():
    storage = get_object_storage()
    with SessionLocal() as database:
        membership = database.scalar(select(WorkspaceMembership))
        project = Project(
            workspace_id=membership.workspace_id,
            created_by_user_id=membership.user_id,
            code=f"J{uuid4().hex[:8]}",
            name="Jobs",
        )
        asset = Asset(project=project, code="asset", name="Asset", asset_type="prop")
        stream = Stream(asset=asset, name="model")
        version = Version(stream=stream, number=1, status="uploaded")
        key = f"jobs/{uuid4().hex}/root.usda"
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
            status="available",
        )
        database.add(project)
        database.commit()
        database.refresh(version)
        database.refresh(stored_file)
        return version.id, stored_file.id


def test_job_submission_is_idempotent(client):
    version_id, file_id = seed_version()
    payload = {"stored_file_id": str(file_id), "idempotency_key": "same-request", "profile_name": "default"}

    first = client.post(f"/api/v1/versions/{version_id}/validation-jobs", json=payload)
    second = client.post(f"/api/v1/versions/{version_id}/validation-jobs", json=payload)

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    assert first.json()["status"] == "pending"


def test_pending_job_can_be_cancelled(client):
    version_id, file_id = seed_version()
    created = client.post(
        f"/api/v1/versions/{version_id}/validation-jobs",
        json={"stored_file_id": str(file_id), "idempotency_key": "cancel-me"},
    )
    job_id = created.json()["id"]

    cancelled = client.post(f"/api/v1/validation-jobs/{job_id}/cancel")

    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    assert cancelled.json()["cancelled_at"] is not None


def test_job_list_and_detail_require_version_access(client):
    version_id, file_id = seed_version()
    created = client.post(
        f"/api/v1/versions/{version_id}/validation-jobs",
        json={"stored_file_id": str(file_id), "idempotency_key": "visible"},
    )
    job_id = created.json()["id"]

    listing = client.get(f"/api/v1/versions/{version_id}/validation-jobs")
    detail = client.get(f"/api/v1/validation-jobs/{job_id}")

    assert listing.status_code == 200
    assert [item["id"] for item in listing.json()] == [job_id]
    assert detail.status_code == 200


def test_restart_recovery_requeues_running_job(client):
    version_id, file_id = seed_version()
    client.post(
        f"/api/v1/versions/{version_id}/validation-jobs",
        json={"stored_file_id": str(file_id), "idempotency_key": "recover"},
    )
    with SessionLocal() as database:
        job = database.scalar(select(ValidationJob).where(ValidationJob.idempotency_key == "recover"))
        job.status = "running"
        job.attempt_count = 1
        database.commit()

    ValidationJobWorker(get_object_storage()).recover_abandoned_jobs()

    with SessionLocal() as database:
        job = database.scalar(select(ValidationJob).where(ValidationJob.idempotency_key == "recover"))
        assert job.status == "pending"
        assert job.error_code == "WorkerRestart"
