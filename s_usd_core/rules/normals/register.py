from s_usd_core.contexts import StageHealthContext
from s_usd_core.validation.check_ids import (
    USD_MESH_NORMALS_AUTHORED,
    USD_MESH_NORMALS_FINITE,
    USD_MESH_NORMALS_COUNT_VALID,
    USD_MESH_NORMALS_INTERPOLATION_VALID,
)
from s_usd_core.validation.enums import Severity
from s_usd_core.validation.models import CheckDefinition

from .checks import (
    check_mesh_normals_authored,
    check_mesh_normals_finite,
    check_mesh_normals_count_valid,
    check_mesh_normals_interpolation_valid,
)


def register_normals_checks(registry):
    entries = (
        (USD_MESH_NORMALS_AUTHORED, "Mesh Normals Authored", check_mesh_normals_authored, Severity.WARNING),
        (USD_MESH_NORMALS_FINITE, "Mesh Normals Finite", check_mesh_normals_finite, Severity.ERROR),
        (USD_MESH_NORMALS_COUNT_VALID, "Mesh Normals Count Valid", check_mesh_normals_count_valid, Severity.ERROR),
        (USD_MESH_NORMALS_INTERPOLATION_VALID, "Mesh Normals Interpolation Valid", check_mesh_normals_interpolation_valid, Severity.WARNING),
    )

    for check_id, label, func, severity in entries:
        registry.register(CheckDefinition(
            check_id=check_id,
            label=label,
            description=label,
            func=func,
            target_type=StageHealthContext,
            category="Normals",
            phase="geometry",
            default_severity=severity,
            tags=("normals", "publish"),
        ))
