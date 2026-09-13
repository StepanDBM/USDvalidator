from pathlib import Path

from validation.check_ids import (
    USD_GEOMETRY_HAS_MATERIAL_BINDING,
    USD_MATERIAL_SURFACE_OUTPUT_CONNECTED,
    USD_MESH_NORMALS_COUNT_VALID,
    USD_MESH_UV_INDICES_VALID,
    USD_SHADER_IDS_ALLOWED,
    USD_SHADER_OUTPUTS_AUTHORED,
)
from validation.enums import CheckStatus
from validation.profiles import ValidationProfile
from validation.publish_checker import PublishChecker
from validation.rule_config import ValidationRuleConfig

FIXTURES = Path(__file__).parent / "fixtures"
CHECKS = frozenset({
    USD_GEOMETRY_HAS_MATERIAL_BINDING,
    USD_MATERIAL_SURFACE_OUTPUT_CONNECTED,
    USD_MESH_NORMALS_COUNT_VALID,
    USD_MESH_UV_INDICES_VALID,
    USD_SHADER_IDS_ALLOWED,
    USD_SHADER_OUTPUTS_AUTHORED,
})


def _results(path):
    profile = ValidationProfile(name="lookdev_test", enabled_check_ids=CHECKS)

    config = ValidationRuleConfig()
    config.materials.require_surface_output = True
    config.materials.require_bindings_on_meshes = True
    config.shaders.require_id = True
    config.shaders.require_outputs = True

    report = PublishChecker(profile=profile, rule_config=config).check(path)
    return {
        result.check_id: result.status
        for result in report.results
    }


def test_valid_lookdev_stage_passes_selected_checks():
    assert all(status is CheckStatus.PASSED for status in _results(FIXTURES / "valid_lookdev.usda").values())


def test_invalid_lookdev_stage_fails_expected_checks():
    results = _results(FIXTURES / "invalid_lookdev.usda")

    assert (
        results[USD_MESH_NORMALS_COUNT_VALID]
        is CheckStatus.FAILED
    )
    assert (
        results[USD_MESH_UV_INDICES_VALID]
        is CheckStatus.FAILED
    )
    assert (
        results[USD_GEOMETRY_HAS_MATERIAL_BINDING]
        is CheckStatus.FAILED
    )
    assert (
        results[USD_MATERIAL_SURFACE_OUTPUT_CONNECTED]
        is CheckStatus.FAILED
    )
    assert (
        results[USD_SHADER_IDS_ALLOWED]
        is CheckStatus.FAILED
    )
    assert (
        results[USD_SHADER_OUTPUTS_AUTHORED]
        is CheckStatus.FAILED
    )