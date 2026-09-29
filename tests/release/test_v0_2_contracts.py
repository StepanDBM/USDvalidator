import json
from pathlib import Path

from s_usd_core.validation.version import (
    MANIFEST_SCHEMA_NAME,
    MANIFEST_SCHEMA_VERSION,
    REPORT_SCHEMA_NAME,
    REPORT_SCHEMA_VERSION,
)
from s_usd_service.config import ServiceSettings

ROOT = Path(__file__).resolve().parents[2]


def test_release_version_is_v0_2_0():
    assert ServiceSettings().service_version == "0.2.0"


def test_v0_2_contract_artifacts_exist():
    required = (
        "docs/v0_2_release_contract.md",
        "docs/v0_2_readiness_report.md",
        "docs/v0_2_threat_review.md",
        "docs/storage_providers.md",
        "docs/validation_jobs.md",
        "docs/project_administration.md",
    )
    assert all((ROOT / path).is_file() for path in required)


def test_existing_report_and_manifest_schemas_remain_readable():
    legacy_report = json.loads((ROOT / "report.json").read_text(encoding="utf-8-sig"))
    legacy_batch = json.loads((ROOT / "batch_report.json").read_text(encoding="utf-8-sig"))

    assert legacy_report["schema_version"]
    assert {"source", "summary", "results"} <= legacy_report.keys()
    assert legacy_batch["schema_version"]
    assert {"batch", "reports"} <= legacy_batch.keys()
    assert (REPORT_SCHEMA_NAME, REPORT_SCHEMA_VERSION) == ("s-usdv.validation_report", "1.0.0")
    assert (MANIFEST_SCHEMA_NAME, MANIFEST_SCHEMA_VERSION) == ("s-usdv.publish_manifest", "1.0.0")
