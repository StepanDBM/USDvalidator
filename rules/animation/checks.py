# rules/animation/checks.py

from validation.check_ids import *
from validation.enums import CheckStatus
from validation.models import CheckResult

def _result(check_id, label, category, runtime, passed, message, details=None, suggestion=""):
    return [CheckResult(
        check_id=check_id, label=label, category=category,
        status=CheckStatus.PASSED if passed else CheckStatus.FAILED,
        severity=runtime.default_severity, message=message,
        suggestion=suggestion, details=details or {},
    )]


def check_stage_frame_range_valid(context, runtime_context):
    start, end = context.stage.start_time_code, context.stage.end_time_code
    return _result(USD_STAGE_FRAME_RANGE_VALID, "Stage Frame Range Valid", "Animation", runtime_context, start is not None and end is not None and start <= end, f"Frame range {start} to {end}.", suggestion="Author a valid frame range.")

def check_animation_frame_rate_valid(context, runtime_context):
    fps = context.stage.frames_per_second
    allowed = runtime_context.config.animation.allowed_frame_rates
    return _result(USD_ANIMATION_FRAME_RATE_VALID, "Animation Frame Rate Valid", "Animation", runtime_context, fps in allowed, f"Frame rate {fps}; allowed {allowed}.", {"fps": fps, "allowed": list(allowed)}, "Use an allowed frame rate.")

def check_animation_has_no_invalid_time_samples(context, runtime_context):
    invalid = context.animation.invalid_time_samples
    return _result(USD_ANIMATION_HAS_NO_INVALID_TIME_SAMPLES, "Animation Has No Invalid Time Samples", "Animation", runtime_context, not invalid, f"Invalid time samples: {len(invalid)}.", {"samples": invalid}, "Repair invalid time samples.")

def check_frame_range_length_limit(context, runtime_context):
    start, end = context.stage.start_time_code, context.stage.end_time_code
    length = max(0, end - start + 1) if start is not None and end is not None else 0
    limit = runtime_context.config.animation.maximum_frame_range
    return _result(USD_FRAME_RANGE_LENGTH_LIMIT, "Frame Range Length Limit", "Animation", runtime_context, length <= limit, f"Frame range length {length}; allowed maximum {limit}.", {"length": length, "limit": limit}, "Reduce the frame range or override the limit.")

def check_time_sample_count_limit(context, runtime_context):
    count = context.animation.time_sample_count
    limit = runtime_context.config.animation.maximum_time_samples
    return _result(USD_TIME_SAMPLE_COUNT_LIMIT, "Time Sample Count Limit", "Animation", runtime_context, count <= limit, f"Time samples {count}; allowed maximum {limit}.", {"count": count, "limit": limit}, "Reduce authored time samples or override the limit.")
