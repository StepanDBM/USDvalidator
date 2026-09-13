from contexts import StageHealthContext
from validation.check_ids import *
from validation.enums import Severity
from validation.models import CheckDefinition
from .checks import *


def register_animation_checks(registry):
    entries = (
        (USD_STAGE_FRAME_RANGE_VALID, "Stage Frame Range Valid", check_stage_frame_range_valid, Severity.ERROR, ("animation", "timing")),
        (USD_ANIMATION_FRAME_RATE_VALID, "Animation Frame Rate Valid", check_animation_frame_rate_valid, Severity.ERROR, ("animation", "timing")),
        (USD_ANIMATION_HAS_NO_INVALID_TIME_SAMPLES, "Animation Has No Invalid Time Samples", check_animation_has_no_invalid_time_samples, Severity.ERROR, ("animation", "samples")),
        (USD_FRAME_RANGE_LENGTH_LIMIT, "Frame Range Length Limit", check_frame_range_length_limit, Severity.WARNING, ("animation", "timing", "budget")),
        (USD_TIME_SAMPLE_COUNT_LIMIT, "Time Sample Count Limit", check_time_sample_count_limit, Severity.WARNING, ("animation", "samples", "budget")),
    )
    for check_id, label, func, severity, tags in entries:
        registry.register(CheckDefinition(check_id=check_id, label=label, description=label, func=func, target_type=StageHealthContext, category="Animation", phase="metadata", default_severity=severity, tags=tags))
