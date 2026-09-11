# rules/animation/checks.py

from validation.enums import CheckStatus
from validation.models import CheckResult

from validation.check_ids import (
    USD_STAGE_FRAME_RANGE_VALID,
    USD_ANIMATION_FRAME_RATE_VALID,
    USD_ANIMATION_HAS_NO_INVALID_TIME_SAMPLES
)


def check_stage_frame_range_valid(context, runtime_context):
    start = context.stage.start_time_code
    end = context.stage.end_time_code

    if start is None or end is None:
        return [CheckResult(
            check_id=USD_STAGE_FRAME_RANGE_VALID,
            label="Stage Frame Range Valid",
            category="Animation",
            status=CheckStatus.FAILED,
            severity=runtime_context.default_severity,
            message="The stage does not define a complete frame range.",
            suggestion="Define both startTimeCode and endTimeCode before publishing.",
            details={
                "start_time_code": start,
                "end_time_code": end,
            },
        )]

    if start > end:
        return [CheckResult(
            check_id=USD_STAGE_FRAME_RANGE_VALID,
            label="Stage Frame Range Valid",
            category="Animation",
            status=CheckStatus.FAILED,
            severity=runtime_context.default_severity,
            message=f"The stage frame range is invalid: start ({start}) is greater than end ({end}).",
            suggestion="Ensure startTimeCode is less than or equal to endTimeCode.",
            details={
                "start_time_code": start,
                "end_time_code": end,
            },
        )]

    return [CheckResult(
        check_id=USD_STAGE_FRAME_RANGE_VALID,
        label="Stage Frame Range Valid",
        category="Animation",
        status=CheckStatus.PASSED,
        severity=runtime_context.default_severity,
        message=f"The stage frame range is valid: {start} to {end}.",
        details={
            "start_time_code": start,
            "end_time_code": end,
        },
    )]


def check_animation_frame_rate_valid(context, runtime_context):
    fps = context.stage.frames_per_second
    time_codes_per_second = context.stage.time_codes_per_second

    if fps is None or fps <= 0:
        return [CheckResult(
            check_id=USD_ANIMATION_FRAME_RATE_VALID,
            label="Animation Frame Rate Valid",
            category="Animation",
            status=CheckStatus.FAILED,
            severity=runtime_context.default_severity,
            message="The stage does not have a valid frames-per-second value.",
            suggestion="Set framesPerSecond to a value greater than zero.",
            details={
                "frames_per_second": fps,
                "time_codes_per_second": time_codes_per_second,
            },
        )]

    if time_codes_per_second is None or time_codes_per_second <= 0:
        return [CheckResult(
            check_id=USD_ANIMATION_FRAME_RATE_VALID,
            label="Animation Frame Rate Valid",
            category="Animation",
            status=CheckStatus.FAILED,
            severity=runtime_context.default_severity,
            message="The stage does not have a valid time-codes-per-second value.",
            suggestion="Set timeCodesPerSecond to a value greater than zero.",
            details={
                "frames_per_second": fps,
                "time_codes_per_second": time_codes_per_second,
            },
        )]

    return [CheckResult(
        check_id=USD_ANIMATION_FRAME_RATE_VALID,
        label="Animation Frame Rate Valid",
        category="Animation",
        status=CheckStatus.PASSED,
        severity=runtime_context.default_severity,
        message=(
            f"The animation frame rate is valid: "
            f"{fps} FPS at {time_codes_per_second} time codes per second."
        ),
        details={
            "frames_per_second": fps,
            "time_codes_per_second": time_codes_per_second,
        },
    )]


def check_animation_has_no_invalid_time_samples(context, runtime_context):
    invalid_time_samples = context.animation.invalid_time_samples

    if invalid_time_samples:
        return [CheckResult(
            check_id=USD_ANIMATION_HAS_NO_INVALID_TIME_SAMPLES,
            label="Animation Has No Invalid Time Samples",
            category="Animation",
            status=CheckStatus.FAILED,
            severity=runtime_context.default_severity,
            message=(
                f"The stage contains {len(invalid_time_samples)} "
                "invalid animation time sample(s)."
            ),
            suggestion="Ensure animated attributes contain valid, ordered time samples.",
            details={
                "invalid_time_samples": invalid_time_samples,
                "invalid_sample_count": len(invalid_time_samples),
            },
        )]

    return [CheckResult(
        check_id=USD_ANIMATION_HAS_NO_INVALID_TIME_SAMPLES,
        label="Animation Has No Invalid Time Samples",
        category="Animation",
        status=CheckStatus.PASSED,
        severity=runtime_context.default_severity,
        message="No invalid animation time samples were detected.",
        details={
            "invalid_sample_count": 0,
        },
    )]