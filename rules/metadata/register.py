# rules/stage/register.py

from contexts import StageHealthContext
from validation.enums import Severity
from validation.models import CheckDefinition

from .checks import (
    check_default_prim_authored,
    check_default_prim_valid,
)
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

    registry.register(CheckDefinition(
        check_id="USD_DEFAULT_PRIM_VALID",
        label="Default Prim Valid",
        func=check_default_prim_valid,
        target_type=StageHealthContext,
        category="Metadata",
        phase="metadata",
        default_severity=Severity.ERROR,
        tags=("metadata", "publish", "required"),
    ))