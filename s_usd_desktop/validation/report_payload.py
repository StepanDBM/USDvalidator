from datetime import datetime, timedelta, timezone

from s_usd_core.validation.version import (
    REPORT_SCHEMA_VERSION,
    TOOL_NAME,
    TOOL_VERSION
)


def build_validation_run_payload(report, stored_file_id=None):
    report_data = report.to_dict()
    completed_at = _parse_timestamp(report.validation_timestamp_utc)
    duration = max(0.0, float(report.validation_duration_seconds))
    started_at = completed_at - timedelta(seconds=duration)
    summary = report.summary
    return {
        "stored_file_id": str(stored_file_id) if stored_file_id else None,
        "profile_name": report.profile_name or "default",
        "report_schema_version": report_data.get("schema", {}).get(
            "version",
            REPORT_SCHEMA_VERSION
        ),
        "tool_name": report_data.get("generator", {}).get("name", TOOL_NAME),
        "tool_version": report_data.get("generator", {}).get("version", TOOL_VERSION),
        "configuration_fingerprint": report.configuration_fingerprint,
        "check_catalog_fingerprint": report.check_catalog_fingerprint,
        "started_at": _format_timestamp(started_at),
        "completed_at": _format_timestamp(completed_at),
        "duration_seconds": duration,
        "publish_passed": report.publish_passed,
        "summary": {
            "total": summary.total,
            "passed": summary.passed,
            "failed": summary.failed,
            "skipped": summary.skipped,
            "errors": summary.internal_errors,
            "warnings": summary.warnings
        },
        "report": report_data
    }


def _parse_timestamp(value):
    if not value:
        return datetime.now(timezone.utc)

    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _format_timestamp(value):
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
