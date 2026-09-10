# rules/stage/register.py

from contexts import StageContext
from validation.enums import Severity
from validation.models import CheckDefinition

from .checks import check_stage_can_open

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