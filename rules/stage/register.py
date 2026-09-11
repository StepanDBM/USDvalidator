# rules/stage/register.py

from contexts import StageContext, StageHealthContext
from validation.enums import Severity
from validation.models import CheckDefinition

from .checks import (
    check_stage_can_open,
    check_stage_has_prims,
    check_stage_has_root_prim,
)

from validation.check_ids import (
    USD_STAGE_CAN_OPEN,
    USD_STAGE_HAS_PRIMS,
    USD_STAGE_HAS_ROOT_PRIM
)

def register_stage_checks(registry):
    registry.register(CheckDefinition(
        check_id=USD_STAGE_CAN_OPEN,
        label="Stage Can Open",
        description="Checks whether the USD Stage can be opened successfully.",
        func=check_stage_can_open,
        target_type=StageContext,
        category="Stage",
        phase="open",
        default_severity=Severity.ERROR,
        tags=("stage", "publish", "required"),
    ))

    registry.register(CheckDefinition(
        check_id=USD_STAGE_HAS_PRIMS,
        label="Stage Has Prims",
        description="Checks whether the USD Stage contains any scene prims.",
        func=check_stage_has_prims,
        target_type=StageHealthContext,
        category="Stage",
        phase="open",
        default_severity=Severity.ERROR,
        tags=("stage", "structure", "publish", "required"),
    ))

    registry.register(CheckDefinition(
        check_id=USD_STAGE_HAS_ROOT_PRIM,
        label="Stage Has Root Prim",
        description="Checks whether the USD Stage contains at least one root prim.",
        func=check_stage_has_root_prim,
        target_type=StageHealthContext,
        category="Stage",
        phase="open",
        default_severity=Severity.ERROR,
        tags=("stage", "structure", "publish", "required"),
    ))