from s_usd_core.contexts import StageHealthContext
from s_usd_core.validation.check_ids import (
    USD_SINGLE_ROOT_PRIM_REQUIRED,
    USD_REQUIRED_HIERARCHY_PATHS_EXIST,
    USD_MESHES_UNDER_REQUIRED_SCOPE,
    USD_NO_MESHES_AT_PSEUDO_ROOT,
)
from s_usd_core.validation.enums import Severity
from s_usd_core.validation.models import CheckDefinition

from .checks import (
    check_single_root_prim_required,
    check_required_hierarchy_paths_exist,
    check_meshes_under_required_scope,
    check_no_meshes_at_pseudo_root,
)


def register_hierarchy_checks(registry):
    entries = (
        (USD_SINGLE_ROOT_PRIM_REQUIRED, "Single Root Prim Required", check_single_root_prim_required, Severity.ERROR),
        (USD_REQUIRED_HIERARCHY_PATHS_EXIST, "Required Hierarchy Paths Exist", check_required_hierarchy_paths_exist, Severity.ERROR),
        (USD_MESHES_UNDER_REQUIRED_SCOPE, "Meshes Under Required Scope", check_meshes_under_required_scope, Severity.WARNING),
        (USD_NO_MESHES_AT_PSEUDO_ROOT, "No Meshes At Pseudo Root", check_no_meshes_at_pseudo_root, Severity.ERROR),
    )

    for check_id, label, func, severity in entries:
        registry.register(CheckDefinition(
            check_id=check_id,
            label=label,
            description=label,
            func=func,
            target_type=StageHealthContext,
            category="Hierarchy",
            phase="structure",
            default_severity=severity,
            tags=("hierarchy", "publish"),
        ))
