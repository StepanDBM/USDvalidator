# rules/metadata/checks.py

from validation.check_ids import (
    USD_DEFAULT_PRIM_AUTHORED,
    USD_DEFAULT_PRIM_VALID,
    USD_FRAME_RATE_VALID,
    USD_METERS_PER_UNIT_AUTHORED,
    USD_METERS_PER_UNIT_VALID,
    USD_ROOT_PRIM_NAME_VALID,
    USD_ROOT_PRIM_TYPE_VALID,
    USD_TIME_CODES_VALID,
    USD_UP_AXIS_VALID,
)
from validation.enums import CheckStatus
from validation.models import CheckResult


def _result(
    *,
    check_id,
    label,
    category,
    runtime_context,
    passed,
    message,
    details=None,
    suggestion="",
    location="",
):
    return [
        CheckResult(
            check_id=check_id,
            label=label,
            category=category,
            status=(
                CheckStatus.PASSED
                if passed
                else CheckStatus.FAILED
            ),
            severity=runtime_context.default_severity,
            message=message,
            location=location,
            suggestion=suggestion,
            details=details or {},
        )
    ]


def check_default_prim_authored(context, runtime_context):
    default_prim = context.stage.default_prim
    passed = bool(default_prim)

    return [
        CheckResult(
            check_id=USD_DEFAULT_PRIM_AUTHORED,
            label="Default Prim Authored",
            category="Metadata",
            status=(
                CheckStatus.PASSED
                if passed
                else CheckStatus.FAILED
            ),
            severity=runtime_context.default_severity,
            message=(
                f"The stage has an authored default prim: {default_prim}."
                if passed
                else "The stage does not have an authored default prim."
            ),
            location=default_prim,
            suggestion=(
                ""
                if passed
                else "Author defaultPrim metadata on the stage."
            ),
            details={
                "default_prim": default_prim,
            },
        )
    ]


def check_default_prim_valid(context, runtime_context):
    default_prim = context.stage.default_prim
    valid = context.stage.default_prim_valid

    if not default_prim:
        return [
            CheckResult(
                check_id=USD_DEFAULT_PRIM_VALID,
                label="Default Prim Valid",
                category="Metadata",
                status=CheckStatus.SKIPPED,
                severity=runtime_context.default_severity,
                message="No defaultPrim is authored.",
                details={
                    "default_prim": "",
                    "valid": None,
                },
            )
        ]

    passed = valid is True

    return [
        CheckResult(
            check_id=USD_DEFAULT_PRIM_VALID,
            label="Default Prim Valid",
            category="Metadata",
            status=(
                CheckStatus.PASSED
                if passed
                else CheckStatus.FAILED
            ),
            severity=runtime_context.default_severity,
            message=(
                f"The authored default prim resolves: {default_prim}."
                if passed
                else (
                    "The authored default prim does not resolve: "
                    f"{default_prim}."
                )
            ),
            location=default_prim,
            suggestion=(
                ""
                if passed
                else "Point defaultPrim at an existing root prim."
            ),
            details={
                "default_prim": default_prim,
                "valid": valid,
            },
        )
    ]


def check_up_axis_valid(context, runtime_context):
    value = context.stage.up_axis
    allowed = runtime_context.config.metadata.allowed_up_axes
    passed = value in allowed

    return _result(
        check_id=USD_UP_AXIS_VALID,
        label="Up Axis Valid",
        category="Metadata",
        runtime_context=runtime_context,
        passed=passed,
        message=(
            f"Up axis {value}; allowed values: {allowed}."
        ),
        details={
            "up_axis": value,
            "allowed": list(allowed),
        },
        suggestion=(
            ""
            if passed
            else "Set an allowed stage up axis."
        ),
    )


def check_meters_per_unit_authored(context, runtime_context):
    value = context.stage.meters_per_unit
    passed = value is not None and value > 0

    return _result(
        check_id=USD_METERS_PER_UNIT_AUTHORED,
        label="Meters Per Unit Authored",
        category="Metadata",
        runtime_context=runtime_context,
        passed=passed,
        message=f"metersPerUnit: {value}.",
        details={
            "meters_per_unit": value,
        },
        suggestion=(
            ""
            if passed
            else "Author a positive metersPerUnit value."
        ),
    )


def check_meters_per_unit_valid(context, runtime_context):
    value = context.stage.meters_per_unit
    minimum = (
        runtime_context
        .config
        .metadata
        .minimum_meters_per_unit
    )
    maximum = (
        runtime_context
        .config
        .metadata
        .maximum_meters_per_unit
    )

    passed = (
        value is not None
        and minimum <= value <= maximum
    )

    return _result(
        check_id=USD_METERS_PER_UNIT_VALID,
        label="Meters Per Unit Valid",
        category="Metadata",
        runtime_context=runtime_context,
        passed=passed,
        message=(
            f"metersPerUnit {value}; allowed range "
            f"{minimum} to {maximum}."
        ),
        details={
            "value": value,
            "minimum": minimum,
            "maximum": maximum,
        },
        suggestion=(
            ""
            if passed
            else "Use a profile-approved world scale."
        ),
    )


def check_root_prim_name_valid(context, runtime_context):
    value = context.stage.root_prim_name
    required = (
        runtime_context
        .config
        .metadata
        .required_root_prim_name
    )
    passed = value == required

    return _result(
        check_id=USD_ROOT_PRIM_NAME_VALID,
        label="Root Prim Name Valid",
        category="Metadata",
        runtime_context=runtime_context,
        passed=passed,
        message=(
            f"Root prim name {value!r}; "
            f"required name {required!r}."
        ),
        location=context.stage.default_prim,
        details={
            "value": value,
            "required": required,
        },
        suggestion=(
            ""
            if passed
            else (
                "Rename the default root prim or override "
                "the required name."
            )
        ),
    )


def check_root_prim_type_valid(context, runtime_context):
    value = context.stage.root_prim_type
    allowed = (
        runtime_context
        .config
        .metadata
        .allowed_root_prim_types
    )
    passed = value in allowed

    return _result(
        check_id=USD_ROOT_PRIM_TYPE_VALID,
        label="Root Prim Type Valid",
        category="Metadata",
        runtime_context=runtime_context,
        passed=passed,
        message=(
            f"Root prim type {value!r}; "
            f"allowed types: {allowed}."
        ),
        location=context.stage.default_prim,
        details={
            "value": value,
            "allowed": list(allowed),
        },
        suggestion=(
            ""
            if passed
            else "Use an allowed root prim type."
        ),
    )


def check_time_codes_valid(context, runtime_context):
    start = context.stage.start_time_code
    end = context.stage.end_time_code

    passed = (
        start is not None
        and end is not None
        and start <= end
    )

    return _result(
        check_id=USD_TIME_CODES_VALID,
        label="Time Codes Valid",
        category="Metadata",
        runtime_context=runtime_context,
        passed=passed,
        message=(
            f"Time codes range from {start} to {end}."
        ),
        details={
            "start_time_code": start,
            "end_time_code": end,
        },
        suggestion=(
            ""
            if passed
            else "Author an ordered time-code range."
        ),
    )


def check_frame_rate_valid(context, runtime_context):
    fps = context.stage.frames_per_second
    time_codes_per_second = (
        context.stage.time_codes_per_second
    )
    allowed = (
        runtime_context
        .config
        .animation
        .allowed_frame_rates
    )

    rates_match = (
        fps is not None
        and time_codes_per_second is not None
        and abs(fps - time_codes_per_second) < 0.0001
    )

    passed = (
        fps in allowed
        and time_codes_per_second in allowed
        and rates_match
    )

    return _result(
        check_id=USD_FRAME_RATE_VALID,
        label="Frame Rate Valid",
        category="Metadata",
        runtime_context=runtime_context,
        passed=passed,
        message=(
            f"Frames per second: {fps}; "
            f"time codes per second: {time_codes_per_second}; "
            f"allowed rates: {allowed}."
        ),
        details={
            "frames_per_second": fps,
            "time_codes_per_second": time_codes_per_second,
            "rates_match": rates_match,
            "allowed": list(allowed),
        },
        suggestion=(
            ""
            if passed
            else "Use an allowed, matching frame rate."
        ),
    )