from datetime import datetime, timezone
from uuid import uuid4

from s_usd_core.validation.enums import CheckStatus, Severity
from s_usd_core.validation.models import CheckResult
from s_usd_core.validation.publish_report import PublishReport
from s_usd_desktop.validation import build_validation_run_payload


def test_serializes_publish_report_for_service():
    report = PublishReport(
        source_path="C:/cache/root/scene.usda",
        stage_opened=True,
        root_layer="C:/cache/root/scene.usda",
        results=[
            CheckResult(
                check_id="PASS",
                label="Pass",
                category="Stage",
                status=CheckStatus.PASSED,
                severity=Severity.ERROR,
                message="Passed"
            ),
            CheckResult(
                check_id="WARN",
                label="Warning",
                category="Geometry",
                status=CheckStatus.FAILED,
                severity=Severity.WARNING,
                message="Warning"
            )
        ],
        validation_timestamp_utc="2026-09-21T14:00:01.250000Z",
        validation_duration_seconds=1.25,
        profile_name="production/default",
        configuration_fingerprint="a" * 64,
        check_catalog_fingerprint="b" * 64
    )
    stored_file_id = uuid4()

    payload = build_validation_run_payload(report, stored_file_id)

    assert payload["stored_file_id"] == str(stored_file_id)
    assert payload["started_at"] == "2026-09-21T14:00:00Z"
    assert payload["completed_at"] == "2026-09-21T14:00:01.250000Z"
    assert payload["summary"] == {
        "total": 2,
        "passed": 1,
        "failed": 1,
        "skipped": 0,
        "errors": 0,
        "warnings": 1
    }
    assert payload["report"]["schema"]["version"] == payload["report_schema_version"]
    assert payload["report"]["results"][1]["check_id"] == "WARN"


def test_missing_timestamp_uses_timezone_aware_utc():
    report = PublishReport("scene.usda", True, "scene.usda")
    payload = build_validation_run_payload(report)

    completed = datetime.fromisoformat(payload["completed_at"].replace("Z", "+00:00"))
    assert completed.tzinfo == timezone.utc
