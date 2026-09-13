from contexts import StageContext, StageHealthContext
from validation.check_ids import *
from validation.enums import Severity
from validation.models import CheckDefinition
from .checks import *


def register_stage_checks(registry):
    entries = (
        (USD_STAGE_CAN_OPEN, "Stage Can Open", check_stage_can_open, StageContext, "open", Severity.ERROR, ("stage", "publish", "required")),
        (USD_STAGE_HAS_PRIMS, "Stage Has Prims", check_stage_has_prims, StageHealthContext, "open", Severity.ERROR, ("stage", "hierarchy", "publish")),
        (USD_STAGE_HAS_ROOT_PRIM, "Stage Has Root Prim", check_stage_has_root_prim, StageHealthContext, "open", Severity.ERROR, ("stage", "hierarchy", "publish")),
        (USD_STAGE_PRIM_COUNT_LIMIT, "Stage Prim Count Limit", check_stage_prim_count_limit, StageHealthContext, "metadata", Severity.WARNING, ("stage", "hierarchy", "budget")),
        (USD_STAGE_PRIM_DEPTH_LIMIT, "Stage Prim Depth Limit", check_stage_prim_depth_limit, StageHealthContext, "metadata", Severity.WARNING, ("stage", "hierarchy", "budget")),
    )

    for check_id, label, func, target, phase, severity, tags in entries:
        registry.register(CheckDefinition(
            check_id=check_id, label=label, description=func.__doc__ or label,
            func=func, target_type=target, category="Stage", phase=phase,
            default_severity=severity, tags=tags,
        ))
