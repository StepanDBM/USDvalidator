from s_usd_desktop.client.models import ValidationRunRecord


class ValidationClient:
    def __init__(self, api):
        self.api = api

    def create_run(self, version_id, payload):
        data = self.api.post(
            f"/api/v1/versions/{version_id}/validation-runs",
            json=payload
        )
        return ValidationRunRecord.from_dict(data)

    def list_runs(self, version_id):
        data = self.api.get(f"/api/v1/versions/{version_id}/validation-runs")
        return tuple(ValidationRunRecord.from_dict(item) for item in data)

    def get_run(self, run_id):
        data = self.api.get(f"/api/v1/validation-runs/{run_id}")
        return ValidationRunRecord.from_dict(data)
