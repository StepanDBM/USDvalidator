from contexts import StageHealthContext
from validation.check_ids import (
    USD_MATERIAL_COUNT_LIMIT,
    USD_MATERIAL_SURFACE_OUTPUT_CONNECTED,
    USD_GEOMETRY_HAS_MATERIAL_BINDING,
    USD_MATERIAL_BINDINGS_RESOLVE,
    USD_MATERIALS_UNDER_REQUIRED_SCOPE,
)
from validation.enums import Severity
from validation.models import CheckDefinition

from .checks import (
    check_material_count_limit,
    check_material_surface_output_connected,
    check_geometry_has_material_binding,
    check_material_bindings_resolve,
    check_materials_under_required_scope,
)


def register_materials_checks(registry):
    entries = (
        (USD_MATERIAL_COUNT_LIMIT, "Material Count Limit", check_material_count_limit, Severity.WARNING),
        (USD_MATERIAL_SURFACE_OUTPUT_CONNECTED, "Material Surface Output Connected", check_material_surface_output_connected, Severity.ERROR),
        (USD_GEOMETRY_HAS_MATERIAL_BINDING, "Geometry Has Material Binding", check_geometry_has_material_binding, Severity.WARNING),
        (USD_MATERIAL_BINDINGS_RESOLVE, "Material Bindings Resolve", check_material_bindings_resolve, Severity.ERROR),
        (USD_MATERIALS_UNDER_REQUIRED_SCOPE, "Materials Under Required Scope", check_materials_under_required_scope, Severity.WARNING),
    )

    for check_id, label, func, severity in entries:
        registry.register(CheckDefinition(
            check_id=check_id,
            label=label,
            description=label,
            func=func,
            target_type=StageHealthContext,
            category="Materials",
            phase="shading",
            default_severity=severity,
            tags=("materials", "publish"),
        ))
