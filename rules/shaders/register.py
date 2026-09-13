from contexts import StageHealthContext
from validation.check_ids import (
    USD_SHADER_COUNT_LIMIT,
    USD_SHADER_ID_AUTHORED,
    USD_SHADER_IDS_ALLOWED,
    USD_SHADER_OUTPUTS_AUTHORED,
    USD_SHADER_ASSET_PATHS_RELATIVE,
)
from validation.enums import Severity
from validation.models import CheckDefinition

from .checks import (
    check_shader_count_limit,
    check_shader_id_authored,
    check_shader_ids_allowed,
    check_shader_outputs_authored,
    check_shader_asset_paths_relative,
)


def register_shaders_checks(registry):
    entries = (
        (USD_SHADER_COUNT_LIMIT, "Shader Count Limit", check_shader_count_limit, Severity.WARNING),
        (USD_SHADER_ID_AUTHORED, "Shader ID Authored", check_shader_id_authored, Severity.ERROR),
        (USD_SHADER_IDS_ALLOWED, "Shader IDs Allowed", check_shader_ids_allowed, Severity.ERROR),
        (USD_SHADER_OUTPUTS_AUTHORED, "Shader Outputs Authored", check_shader_outputs_authored, Severity.ERROR),
        (USD_SHADER_ASSET_PATHS_RELATIVE, "Shader Asset Paths Relative", check_shader_asset_paths_relative, Severity.ERROR),
    )

    for check_id, label, func, severity in entries:
        registry.register(CheckDefinition(
            check_id=check_id,
            label=label,
            description=label,
            func=func,
            target_type=StageHealthContext,
            category="Shaders",
            phase="shading",
            default_severity=severity,
            tags=("shaders", "publish"),
        ))
