from s_usd_core.contexts import StageHealthContext
from s_usd_core.validation.check_ids import (
    USD_MESH_UV_SET_REQUIRED,
    USD_MESH_UV_SET_COUNT_LIMIT,
    USD_MESH_UV_INDICES_VALID,
    USD_MESH_UV_INTERPOLATION_VALID,
)
from s_usd_core.validation.enums import Severity
from s_usd_core.validation.models import CheckDefinition

from .checks import (
    check_mesh_uv_set_required,
    check_mesh_uv_set_count_limit,
    check_mesh_uv_indices_valid,
    check_mesh_uv_interpolation_valid,
)


def register_uvs_checks(registry):
    entries = (
        (USD_MESH_UV_SET_REQUIRED, "Mesh UV Set Required", check_mesh_uv_set_required, Severity.WARNING),
        (USD_MESH_UV_SET_COUNT_LIMIT, "Mesh UV Set Count Limit", check_mesh_uv_set_count_limit, Severity.WARNING),
        (USD_MESH_UV_INDICES_VALID, "Mesh UV Indices Valid", check_mesh_uv_indices_valid, Severity.ERROR),
        (USD_MESH_UV_INTERPOLATION_VALID, "Mesh UV Interpolation Valid", check_mesh_uv_interpolation_valid, Severity.WARNING),
    )

    for check_id, label, func, severity in entries:
        registry.register(CheckDefinition(
            check_id=check_id,
            label=label,
            description=label,
            func=func,
            target_type=StageHealthContext,
            category="UVs",
            phase="geometry",
            default_severity=severity,
            tags=("uvs", "publish"),
        ))
