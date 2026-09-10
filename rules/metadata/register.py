# rules/stage/register.py

from contexts import StageHealthContext
from validation.enums import Severity
from validation.models import CheckDefinition

from .checks import (
    check_default_prim_authored,
    check_default_prim_valid,
    check_up_axis_valid,
    check_meters_per_unit_authored,
    check_time_codes_valid,
    check_frame_rate_valid,
)


def register_metadata_checks(registry):
    registry.register(CheckDefinition(
        check_id="USD_DEFAULT_PRIM_AUTHORED",
        label="Default Prim Authored",
        description="Checks whether the stage has an authored defaultPrim.",
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
        description="Checks whether the authored defaultPrim resolves to a valid prim.",
        func=check_default_prim_valid,
        target_type=StageHealthContext,
        category="Metadata",
        phase="metadata",
        default_severity=Severity.ERROR,
        tags=("metadata", "publish", "required"),
    ))


def register_metadata_checks(registry):
    registry.register(CheckDefinition(
        check_id="USD_DEFAULT_PRIM_AUTHORED",
        label="Default Prim Authored",
        description="Checks whether the stage has an authored defaultPrim.",
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
        description="Checks whether the authored defaultPrim resolves to a valid prim.",
        func=check_default_prim_valid,
        target_type=StageHealthContext,
        category="Metadata",
        phase="metadata",
        default_severity=Severity.ERROR,
        tags=("metadata", "publish", "required"),
    ))

    registry.register(CheckDefinition(
        check_id="USD_UP_AXIS_VALID",
        label="Up Axis Valid",
        description="Checks whether the stage uses a valid USD up axis.",
        func=check_up_axis_valid,
        target_type=StageHealthContext,
        category="Metadata",
        phase="metadata",
        default_severity=Severity.ERROR,
        tags=("metadata", "publish", "required"),
    ))

    registry.register(CheckDefinition(
        check_id="USD_METERS_PER_UNIT_AUTHORED",
        label="Meters Per Unit Authored",
        description="Checks whether the stage has a valid metersPerUnit value.",
        func=check_meters_per_unit_authored,
        target_type=StageHealthContext,
        category="Metadata",
        phase="metadata",
        default_severity=Severity.ERROR,
        tags=("metadata", "publish", "required"),
    ))

    registry.register(CheckDefinition(
        check_id="USD_TIME_CODES_VALID",
        label="Time Codes Valid",
        description="Checks whether the stage has a valid start and end time-code range.",
        func=check_time_codes_valid,
        target_type=StageHealthContext,
        category="Metadata",
        phase="metadata",
        default_severity=Severity.ERROR,
        tags=("metadata", "publish", "required"),
    ))

    registry.register(CheckDefinition(
        check_id="USD_FRAME_RATE_VALID",
        label="Frame Rate Valid",
        description="Checks whether the stage has valid framesPerSecond and timeCodesPerSecond values.",
        func=check_frame_rate_valid,
        target_type=StageHealthContext,
        category="Metadata",
        phase="metadata",
        default_severity=Severity.ERROR,
        tags=("metadata", "publish", "required"),
    ))