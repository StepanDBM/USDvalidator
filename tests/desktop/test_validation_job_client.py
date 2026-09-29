from datetime import datetime, timezone
from uuid import uuid4

from s_usd_desktop.client.validation_client import ValidationClient


def job_payload(**overrides):
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "id": str(uuid4()),
        "workspace_id": str(uuid4()),
        "version_id": str(uuid4()),
        "stored_file_id": str(uuid4()),
        "requested_by_user_id": str(uuid4()),
        "validation_run_id": None,
        "idempotency_key": "desktop-request",
        "profile_name": "default",
        "status": "running",
        "progress_current": 1,
        "progress_total": 4,
        "attempt_count": 1,
        "maximum_attempts": 3,
        "requested_at": now,
        "started_at": now,
        "completed_at": None,
        "cancelled_at": None,
        "heartbeat_at": now,
        "next_attempt_at": None,
        "error_code": "",
        "error_message": "",
        "created_at": now,
        "updated_at": now,
    }
    payload.update(overrides)
    return payload


class Api:
    def __init__(self):
        self.calls = []

    def post(self, path, json=None):
        self.calls.append(("POST", path, json))
        return job_payload()

    def get(self, path):
        self.calls.append(("GET", path, None))
        return job_payload()


def test_create_job_sends_idempotency_payload_and_parses_progress():
    api = Api()
    client = ValidationClient(api)
    version_id, file_id = uuid4(), uuid4()

    job = client.create_job(version_id, file_id, "desktop-request")

    assert api.calls[0][1] == f"/api/v1/versions/{version_id}/validation-jobs"
    assert api.calls[0][2]["stored_file_id"] == str(file_id)
    assert job.progress_percent == 25
    assert not job.terminal


def test_get_and_cancel_job_use_job_endpoints():
    api = Api()
    client = ValidationClient(api)
    job_id = uuid4()

    client.get_job(job_id)
    client.cancel_job(job_id)

    assert api.calls == [
        ("GET", f"/api/v1/validation-jobs/{job_id}", None),
        ("POST", f"/api/v1/validation-jobs/{job_id}/cancel", None),
    ]
