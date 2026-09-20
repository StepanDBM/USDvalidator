from pathlib import Path

from s_usd_core.validation import CheckStatus, PublishChecker
from s_usd_core.validation.attribute_override import AttributeOverride
from s_usd_core.validation.check_ids import (
    USD_ASSET_PATHS_RELATIVE,
    USD_FRAME_RANGE_LENGTH_LIMIT,
    USD_METERS_PER_UNIT_VALID,
    USD_PAYLOADS_ALLOWED,
    USD_ROOT_PRIM_NAME_VALID,
    USD_ROOT_PRIM_TYPE_VALID,
)
from s_usd_core.validation.profiles import ValidationProfile

FIXTURE = Path(__file__).parent / "fixtures" / "invalid_policy.usda"


def get_result(report, check_id):
    return next(item for item in report.results if item.check_id == check_id)


def test_invalid_policy_fixture_reports_expected_policy_results():
    report = PublishChecker().check(FIXTURE)

    for check_id in (
        USD_METERS_PER_UNIT_VALID,
        USD_ROOT_PRIM_TYPE_VALID,
        USD_FRAME_RANGE_LENGTH_LIMIT,
        USD_ASSET_PATHS_RELATIVE,
    ):
        assert get_result(report, check_id).status is CheckStatus.FAILED


def test_payload_policy_override_rejects_payloads():
    profile = ValidationProfile(
        name="no_payloads",
        enabled_check_ids=frozenset({USD_PAYLOADS_ALLOWED}),
        overrides=(AttributeOverride("composition.allow_payloads", False),),
    )
    report = PublishChecker(profile=profile).check(FIXTURE)
    assert get_result(report, USD_PAYLOADS_ALLOWED).status is CheckStatus.FAILED


def test_root_name_override_accepts_asset_root():
    profile = ValidationProfile(
        name="asset_root",
        enabled_check_ids=frozenset({USD_ROOT_PRIM_NAME_VALID}),
        overrides=(
            AttributeOverride("metadata.required_root_prim_name", "AssetRoot"),
        ),
    )
    report = PublishChecker(profile=profile).check(FIXTURE)
    assert get_result(report, USD_ROOT_PRIM_NAME_VALID).status is CheckStatus.PASSED
