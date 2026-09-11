# rules/animation/register.py

from contexts import StageHealthContext
from validation.enums import Severity
from validation.models import CheckDefinition

from .checks import (
    check_animation_frame_rate_valid,
    check_animation_has_no_invalid_time_samples,
    check_stage_frame_range_valid,
)

from validation.check_ids import (
    USD_STAGE_FRAME_RANGE_VALID,
    USD_ANIMATION_FRAME_RATE_VALID,
    USD_ANIMATION_HAS_NO_INVALID_TIME_SAMPLES
)



def register_animation_checks(registry):
    registry.register(CheckDefinition(
        check_id=USD_STAGE_FRAME_RANGE_VALID,
        label="Stage Frame Range Valid",
        description="Checks whether the stage defines a valid animation frame range.",
        func=check_stage_frame_range_valid,
        target_type=StageHealthContext,
        category="Animation",
        phase="metadata",
        default_severity=Severity.ERROR,
        tags=("animation", "metadata", "publish", "required"),
    ))

    registry.register(CheckDefinition(
        check_id=USD_ANIMATION_FRAME_RATE_VALID,
        label="Animation Frame Rate Valid",
        description="Checks whether the stage has valid frame-rate metadata.",
        func=check_animation_frame_rate_valid,
        target_type=StageHealthContext,
        category="Animation",
        phase="metadata",
        default_severity=Severity.ERROR,
        tags=("animation", "metadata", "publish", "required"),
    ))

    registry.register(CheckDefinition(
        check_id=USD_ANIMATION_HAS_NO_INVALID_TIME_SAMPLES,
        label="Animation Has No Invalid Time Samples",
        description="Checks whether animated attributes contain valid time samples.",
        func=check_animation_has_no_invalid_time_samples,
        target_type=StageHealthContext,
        category="Animation",
        phase="metadata",
        default_severity=Severity.ERROR,
        tags=("animation", "samples", "publish", "required"),
    ))