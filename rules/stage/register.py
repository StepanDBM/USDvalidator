# rules/stage/register.py

from contexts import StageContext
from contexts import StageHealthContext
from validation.enums import Severity
from validation.models import CheckDefinition

from .checks import check_stage_can_open
from .checks import check_default_prim_authored

def register_stage_checks(registry):
    registry.register(CheckDefinition(
        check_id="USD_STAGE_CAN_OPEN",
        label="Stage Can Open",
        func=check_stage_can_open,
        target_type=StageContext,
        category="Stage",
        phase="open",
        default_severity=Severity.ERROR,
        tags=("stage", "publish", "required")
    ))



def register_metadata_checks(registry):
    registry.register(CheckDefinition(
        check_id="USD_DEFAULT_PRIM_AUTHORED",
        label="Default Prim Authored",
        func=check_default_prim_authored,
        target_type=StageHealthContext,
        category="Metadata",
        phase="metadata",
        default_severity=Severity.ERROR,
        tags=("metadata", "publish", "required"),
    ))