from s_usd_desktop.client.models import ValidationJobRecord, ValidationRunRecord


class ValidationClient:
    def __init__(self, api):
        self.api = api

    def create_run(self, version_id, payload):
        data = self.api.post(f"/api/v1/versions/{version_id}/validation-runs", json=payload)
        return ValidationRunRecord.from_dict(data)

    def list_runs(self, version_id):
        data = self.api.get(f"/api/v1/versions/{version_id}/validation-runs")
        return tuple(ValidationRunRecord.from_dict(item) for item in data)

    def get_run(self, run_id):
        data = self.api.get(f"/api/v1/validation-runs/{run_id}")
        return ValidationRunRecord.from_dict(data)

    def create_job(self, version_id, stored_file_id, idempotency_key, profile_name="default"):
        data = self.api.post(
            f"/api/v1/versions/{version_id}/validation-jobs",
            json={
                "stored_file_id": str(stored_file_id),
                "idempotency_key": idempotency_key,
                "profile_name": profile_name,
            },
        )
        return ValidationJobRecord.from_dict(data)

    def list_jobs(self, version_id):
        data = self.api.get(f"/api/v1/versions/{version_id}/validation-jobs")
        return tuple(ValidationJobRecord.from_dict(item) for item in data)

    def get_job(self, job_id):
        return ValidationJobRecord.from_dict(self.api.get(f"/api/v1/validation-jobs/{job_id}"))

    def cancel_job(self, job_id):
        return ValidationJobRecord.from_dict(self.api.post(f"/api/v1/validation-jobs/{job_id}/cancel"))
