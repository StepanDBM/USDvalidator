from pathlib import Path

from reporting.fingerprint import configuration_fingerprint
from reporting.manifest import PublishManifest
from validation import PublishChecker
from validation.rule_config import ValidationRuleConfig
from validation.version import (
    MANIFEST_SCHEMA_NAME,
    MANIFEST_SCHEMA_VERSION,
    REPORT_SCHEMA_NAME,
    REPORT_SCHEMA_VERSION,
)


FIXTURE = Path(__file__).parent / "fixtures" / "valid_stage.usda"


def test_publish_report_has_versioned_contract():
    data = PublishChecker().check(FIXTURE).to_dict()

    assert data["schema"] == {
        "name": REPORT_SCHEMA_NAME,
        "version": REPORT_SCHEMA_VERSION,
    }
    assert data["generator"]["name"] == "USDvalidator"
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
    report = PublishChecker().check(FIXTURE)
    data = PublishManifest(report).to_dict()

    assert data["schema"] == {
        "name": MANIFEST_SCHEMA_NAME,
        "version": MANIFEST_SCHEMA_VERSION,
    }
    assert data["publish"]["validation_passed"] is True
    assert data["validation"]["configuration_fingerprint"]
