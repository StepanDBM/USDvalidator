# tests/test_config_resolver.pyimport pytest

import pytest

from s_usd_core.validation.attribute_override import AttributeOverride
from s_usd_core.validation.config_resolver import build_effective_config
from s_usd_core.validation.profiles import ValidationProfile
from s_usd_core.validation.rule_config import ValidationRuleConfig

from s_usd_core.validation.check_ids import USD_MESH_POLYGON_COUNT_LIMIT
from s_usd_core.validation.enums import CheckStatus
from s_usd_core.validation.publish_checker import PublishChecker


def find_result(report, check_id):
    return next(
        result
        for result in report.results
        if result.check_id == check_id
    )


def test_polygon_limit_uses_profile_override():
    profile = ValidationProfile(
        name="heavy_geometry",
        enabled_check_ids=frozenset({
            USD_MESH_POLYGON_COUNT_LIMIT,
        }),
        overrides=(
            AttributeOverride(
                path="geometry.polygon_count_limit",
                value=200000,
            ),
        ),
    )

    checker = PublishChecker(profile=profile)
    report = checker.check(
        "tests/fixtures/invalid_geometry_polygon_limit.usda"
    )

    result = find_result(
        report,
        USD_MESH_POLYGON_COUNT_LIMIT,
    )

    assert result.status is CheckStatus.PASSED

def test_polygon_limit_uses_default_without_override():
    profile = ValidationProfile(
        name="default_geometry",
        enabled_check_ids=frozenset({
            USD_MESH_POLYGON_COUNT_LIMIT,
        }),
    )

    checker = PublishChecker(profile=profile)
    report = checker.check(
        "tests/fixtures/invalid_geometry_polygon_limit.usda"
    )

    result = find_result(
        report,
        USD_MESH_POLYGON_COUNT_LIMIT,
    )

    assert result.status is CheckStatus.FAILED


def test_profile_override_changes_effective_config():
    profile = ValidationProfile(
        name="heavy_geometry",
        overrides=(
            AttributeOverride(
                path="geometry.polygon_count_limit",
                value=250000,
            ),
        ),
    )

    config = build_effective_config(profile)

    assert config.geometry.polygon_count_limit == 250000


def test_profile_override_does_not_mutate_base_config():
    base_config = ValidationRuleConfig()
    profile = ValidationProfile(
        name="heavy_geometry",
        overrides=(
            AttributeOverride(
                path="geometry.polygon_count_limit",
                value=250000,
            ),
        ),
    )

    effective_config = build_effective_config(profile, base_config)

    assert base_config.geometry.polygon_count_limit == 100000
    assert effective_config.geometry.polygon_count_limit == 250000


def test_disabled_override_is_ignored():
    profile = ValidationProfile(
        name="disabled_override",
        overrides=(
            AttributeOverride(
                path="geometry.polygon_count_limit",
                value=250000,
                enabled=False,
            ),
        ),
    )

    config = build_effective_config(profile)

    assert config.geometry.polygon_count_limit == 100000


def test_unknown_override_path_is_rejected():
    profile = ValidationProfile(
        name="invalid_override",
        overrides=(
            AttributeOverride(
                path="geometry.not_a_real_setting",
                value=250000,
            ),
        ),
    )

    with pytest.raises(AttributeError):
        build_effective_config(profile)

def test_wrong_override_type_is_rejected():
    profile = ValidationProfile(
        name="invalid_type",
        overrides=(
            AttributeOverride(
                path="geometry.polygon_count_limit",
                value="250000",
            ),
        ),
    )

    with pytest.raises(TypeError):
        build_effective_config(profile)

import json

from s_usd_core.validation.profile_loader import ProfileLoader


def test_profile_overrides_survive_save_and_reload(tmp_path):
    profiles_path = tmp_path / "profiles.json"

    profiles_path.write_text(
        json.dumps({
            "profiles": [
                {
                    "name": "test_profile",
                    "enabled_checks": [],
                    "disabled_checks": [],
                    "overrides": [
                        {
                            "path": "geometry.polygon_count_limit",
                            "value": 250000,
                            "enabled": True,
                        }
                    ],
                }
            ]
        }),
        encoding="utf-8",
    )

    loader = ProfileLoader(profiles_path)
    loader.save()

    reloaded = ProfileLoader(profiles_path)
    profile = reloaded.get_profile("test_profile")
    override = profile.overrides[0]

    assert override.path == "geometry.polygon_count_limit"
    assert override.value == 250000
    assert override.enabled is True