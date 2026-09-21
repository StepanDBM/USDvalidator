import json
from uuid import UUID

import httpx

from s_usd_desktop.client import SUsdvApiClient, ValidationClient

RUN_ID = "11111111-1111-4111-8111-111111111111"
VERSION_ID = "22222222-2222-4222-8222-222222222222"
DATE = "2026-09-21T14:00:00+00:00"


def run_data(include_report=False):
    data = {
        "id": RUN_ID,
        "version_id": VERSION_ID,
        "stored_file_id": None,
        "profile_name": "production/default",
        "report_schema_version": "1.0.0",
        "tool_name": "S-USDv",
        "tool_version": "0.6.0",
        "configuration_fingerprint": "a" * 64,
        "check_catalog_fingerprint": "b" * 64,
        "started_at": DATE,
        "completed_at": DATE,
        "duration_seconds": 1.25,
        "publish_passed": False,
        "total_count": 4,
        "passed_count": 2,
        "failed_count": 1,
        "skipped_count": 0,
        "error_count": 1,
        "warning_count": 1,
        "created_at": DATE,
        "updated_at": DATE
    }
    if include_report:
        data["report"] = {"results": [{"check_id": "USD_STAGE_CAN_OPEN"}]}
    return data


def test_create_run_sends_payload_and_parses_detail():
    captured = {}

    def handler(request):
        captured["path"] = request.url.path
        captured["payload"] = json.loads(request.content)
        return httpx.Response(201, json=run_data(include_report=True))

    with SUsdvApiClient(transport=httpx.MockTransport(handler)) as api:
        record = ValidationClient(api).create_run(VERSION_ID, {"profile_name": "production/default"})

    assert captured["path"] == f"/api/v1/versions/{VERSION_ID}/validation-runs"
    assert captured["payload"] == {"profile_name": "production/default"}
    assert record.id == UUID(RUN_ID)
    assert record.report["results"][0]["check_id"] == "USD_STAGE_CAN_OPEN"


def test_list_runs_parses_lightweight_records():
    transport = httpx.MockTransport(lambda _: httpx.Response(200, json=[run_data()]))

    with SUsdvApiClient(transport=transport) as api:
        records = ValidationClient(api).list_runs(VERSION_ID)

    assert len(records) == 1
    assert records[0].version_id == UUID(VERSION_ID)
    assert records[0].report is None


def test_get_run_parses_complete_report():
    transport = httpx.MockTransport(
        lambda _: httpx.Response(200, json=run_data(include_report=True))
    )

    with SUsdvApiClient(transport=transport) as api:
        record = ValidationClient(api).get_run(RUN_ID)

    assert record.report == {"results": [{"check_id": "USD_STAGE_CAN_OPEN"}]}
