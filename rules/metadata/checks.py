# rules/metadata/checks.py
from validation.enums import CheckStatus
from validation.models import CheckResult


def check_default_prim_authored(context, runtime_context):
    default_prim = context.stage.default_prim

    if default_prim:
        return [CheckResult(
            check_id="USD_DEFAULT_PRIM_AUTHORED",
            label="Default Prim Authored",
            category="Metadata",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message=f"The stage has an authored default prim: {default_prim}.",
            location=default_prim,
            details={
                "default_prim": default_prim,
            },
        )]

    return [CheckResult(
        check_id="USD_DEFAULT_PRIM_AUTHORED",
        label="Default Prim Authored",
        category="Metadata",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message="The stage does not have an authored default prim.",
        suggestion="Author a valid default prim before publishing.",
        details={
            "default_prim": None,
        },
    )]


def check_default_prim_valid(context, runtime_context):
    default_prim_path = context.stage.default_prim

    if not default_prim_path:
        return [CheckResult(
            check_id="USD_DEFAULT_PRIM_VALID",
            label="Default Prim Valid",
            category="Metadata",
            status=CheckStatus.SKIPPED,
            severity=runtime_context.default_severity,
            message="No defaultPrim is authored; validity cannot be evaluated.",
            details={
                "default_prim": None,
                "valid": None,
            },
        )]

    if context.stage.default_prim_valid:
        return [CheckResult(
            check_id="USD_DEFAULT_PRIM_VALID",
            label="Default Prim Valid",
            category="Metadata",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message="The authored defaultPrim resolves to a valid prim.",
            location=default_prim_path,
            layer=context.stage.root_layer,
            details={
                "default_prim": default_prim_path,
                "valid": True,
            },
        )]

    return [CheckResult(
        check_id="USD_DEFAULT_PRIM_VALID",
        label="Default Prim Valid",
        category="Metadata",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message=(
            f"The authored defaultPrim '{default_prim_path}' "
            "does not resolve to a valid prim."
        ),
        location=default_prim_path,
        layer=context.stage.root_layer,
        suggestion="Set defaultPrim to the path of an existing valid prim.",
        details={
            "default_prim": default_prim_path,
            "valid": False,
        },
    )]

def check_default_prim_authored(context, runtime_context):
    default_prim = context.stage.default_prim

    if default_prim:
        return [CheckResult(
            check_id="USD_DEFAULT_PRIM_AUTHORED",
            label="Default Prim Authored",
            category="Metadata",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message=f"The stage has an authored default prim: {default_prim}.",
            location=default_prim,
        )]

    return [CheckResult(
        check_id="USD_DEFAULT_PRIM_AUTHORED",
        label="Default Prim Authored",
        category="Metadata",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message="The stage does not have an authored default prim.",
        suggestion="Author a valid default prim before publishing.",
    )]


def check_default_prim_valid(context, runtime_context):
    default_prim_path = context.stage.default_prim

    if not default_prim_path:
        return [CheckResult(
            check_id="USD_DEFAULT_PRIM_VALID",
            label="Default Prim Valid",
            category="Metadata",
            status=CheckStatus.SKIPPED,
            severity=runtime_context.default_severity,
            message="No defaultPrim is authored; validity cannot be evaluated."
        )]

    if context.stage.default_prim_valid:
        return [CheckResult(
            check_id="USD_DEFAULT_PRIM_VALID",
            label="Default Prim Valid",
            category="Metadata",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message="The authored defaultPrim resolves to a valid prim.",
            location=default_prim_path,
            layer=context.stage.root_layer,
        )]

    return [CheckResult(
        check_id="USD_DEFAULT_PRIM_VALID",
        label="Default Prim Valid",
        category="Metadata",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message=(
            f"The authored defaultPrim '{default_prim_path}' "
            "does not resolve to a valid prim."
        ),
        location=default_prim_path,
        layer=context.stage.root_layer,
        suggestion="Set defaultPrim to the path of an existing valid prim."
    )]


def check_up_axis_valid(context, runtime_context):
    up_axis = context.stage.up_axis

    if up_axis in {"Y", "Z"}:
        return [CheckResult(
            check_id="USD_UP_AXIS_VALID",
            label="Up Axis Valid",
            category="Metadata",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message=f"The stage uses a valid up axis: {up_axis}.",
            details={
                "up_axis": up_axis,
            },
        )]

    return [CheckResult(
        check_id="USD_UP_AXIS_VALID",
        label="Up Axis Valid",
        category="Metadata",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message=f"The stage has an invalid or undefined up axis: '{up_axis}'.",
        suggestion="Set the stage up axis to Y or Z.",
        details={
            "up_axis": up_axis,
        },
    )]


def check_meters_per_unit_authored(context, runtime_context):
    meters_per_unit = context.stage.meters_per_unit

    if meters_per_unit is not None and meters_per_unit > 0:
        return [CheckResult(
            check_id="USD_METERS_PER_UNIT_AUTHORED",
            label="Meters Per Unit Authored",
            category="Metadata",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message=(
                f"The stage has a valid metersPerUnit value: "
                f"{meters_per_unit}."
            ),
            details={
                "meters_per_unit": meters_per_unit,
            },
        )]

    return [CheckResult(
        check_id="USD_METERS_PER_UNIT_AUTHORED",
        label="Meters Per Unit Authored",
        category="Metadata",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message="The stage does not have a valid metersPerUnit value.",
        suggestion="Author a positive metersPerUnit value on the stage.",
        details={
            "meters_per_unit": meters_per_unit,
        },
    )]


def check_time_codes_valid(context, runtime_context):
    start_time_code = context.stage.start_time_code
    end_time_code = context.stage.end_time_code

    if start_time_code is None or end_time_code is None:
        return [CheckResult(
            check_id="USD_TIME_CODES_VALID",
            label="Time Codes Valid",
            category="Metadata",
            status=CheckStatus.FAILED,
            severity=runtime_context.default_severity,
            message="The stage does not have valid start and end time codes.",
            suggestion="Set valid startTimeCode and endTimeCode metadata.",
            details={
                "start_time_code": start_time_code,
                "end_time_code": end_time_code,
            },
        )]

    if start_time_code <= end_time_code:
        return [CheckResult(
            check_id="USD_TIME_CODES_VALID",
            label="Time Codes Valid",
            category="Metadata",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message=(
                f"The stage has a valid time range: "
                f"{start_time_code} - {end_time_code}."
            ),
            details={
                "start_time_code": start_time_code,
                "end_time_code": end_time_code,
            },
        )]

    return [CheckResult(
        check_id="USD_TIME_CODES_VALID",
        label="Time Codes Valid",
        category="Metadata",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message=(
            f"The stage has an invalid time range: "
            f"{start_time_code} - {end_time_code}."
        ),
        suggestion="Ensure startTimeCode is less than or equal to endTimeCode.",
        details={
            "start_time_code": start_time_code,
            "end_time_code": end_time_code,
        },
    )]


def check_frame_rate_valid(context, runtime_context):
    frames_per_second = context.stage.frames_per_second
    time_codes_per_second = context.stage.time_codes_per_second

    if (
        frames_per_second is not None
        and frames_per_second > 0
        and time_codes_per_second is not None
        and time_codes_per_second > 0
    ):
        return [CheckResult(
            check_id="USD_FRAME_RATE_VALID",
            label="Frame Rate Valid",
            category="Metadata",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message=(
                f"The stage has valid rates: "
                f"{frames_per_second} FPS, "
                f"{time_codes_per_second} timeCodesPerSecond."
            ),
            details={
                "frames_per_second": frames_per_second,
                "time_codes_per_second": time_codes_per_second,
            },
        )]

    return [CheckResult(
        check_id="USD_FRAME_RATE_VALID",
        label="Frame Rate Valid",
        category="Metadata",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message=(
            "The stage does not have valid framesPerSecond and "
            "timeCodesPerSecond values."
        ),
        suggestion=(
            "Set positive framesPerSecond and timeCodesPerSecond "
            "values on the stage."
        ),
        details={
            "frames_per_second": frames_per_second,
            "time_codes_per_second": time_codes_per_second,
        },
    )]