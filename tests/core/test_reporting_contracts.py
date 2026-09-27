from pathlib import Path

from s_usd_core.reporting.fingerprint import configuration_fingerprint
from s_usd_core.reporting.manifest import PublishManifest
from s_usd_core.validation import PublishChecker
from s_usd_core.validation.rule_config import ValidationRuleConfig
from s_usd_core.validation.version import (
    MANIFEST_SCHEMA_NAME,
    MANIFEST_SCHEMA_VERSION,
    REPORT_SCHEMA_NAME,
    REPORT_SCHEMA_VERSION,
)


FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
VALID_FIXTURE = FIXTURES_DIR / "valid_stage.usda"
INVALID_FIXTURE = FIXTURES_DIR / "invalid_policy.usda"


def test_publish_report_has_versioned_contract():
    data = PublishChecker().check(INVALID_FIXTURE).to_dict()

    assert data["schema"] == {
        "name": REPORT_SCHEMA_NAME,
        "version": REPORT_SCHEMA_VERSION,
    }
    assert data["generator"]["name"] == "S-USDv"
    assert data["validation"]["timestamp_utc"].endswith("Z")
    assert len(data["validation"]["profile"]["configuration_fingerprint"]) == 64
    assert len(data["validation"]["check_catalog"]["fingerprint"]) == 64


def test_configuration_fingerprint_is_stable_and_sensitive():
    first = ValidationRuleConfig()
    second = ValidationRuleConfig()

    assert configuration_fingerprint(first) == configuration_fingerprint(second)

    second.geometry.polygon_count_limit += 1

    assert configuration_fingerprint(first) != configuration_fingerprint(second)


def test_manifest_has_versioned_contract():
    report = PublishChecker().check(VALID_FIXTURE)
    data = PublishManifest(report).to_dict()

    assert data["schema"] == {
        "name": MANIFEST_SCHEMA_NAME,
        "version": MANIFEST_SCHEMA_VERSION,
    }
    assert data["publish"]["validation_passed"] is True
    assert data["validation"]["configuration_fingerprint"]