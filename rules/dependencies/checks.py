from validation.enums import CheckStatus
from validation.models import CheckResult

from validation.check_ids import (
    USD_DEPENDENCIES_RESOLVE,
    USD_REFERENCES_RESOLVE,
    USD_PAYLOADS_RESOLVE
)


def check_dependencies_resolve(context, runtime_context):
    unresolved_count = (
        context.composition.unresolved_references
        + context.composition.unresolved_payloads
    )

    if unresolved_count:
        return [CheckResult(
            check_id=USD_DEPENDENCIES_RESOLVE,
            label="USD Dependencies Resolve",
            category="Dependencies",
            status=CheckStatus.FAILED,
            severity=runtime_context.default_severity,
            message=(
                f"The stage contains "
                f"{unresolved_count} unresolved dependency arc(s)."
            ),
            suggestion=(
                "Ensure all referenced and payload layers can be resolved."
            ),
            details={
                "unresolved_dependencies": unresolved_count,
                "unresolved_count": unresolved_count,
            },
        )]

    return [CheckResult(
        check_id=USD_DEPENDENCIES_RESOLVE,
        label="USD Dependencies Resolve",
        category="Dependencies",
        status=CheckStatus.PASSED,
        severity=runtime_context.default_severity,
        message="All USD dependencies resolve successfully.",
        details={"unresolved_count": 0},
    )]


def check_references_resolve(context, runtime_context):
    unresolved_count = context.composition.unresolved_references

    if unresolved_count:
        return [CheckResult(
            check_id=USD_REFERENCES_RESOLVE,
            label="USD References Resolve",
            category="Dependencies",
            status=CheckStatus.FAILED,
            severity=runtime_context.default_severity,
            message=(
                f"The stage contains "
                f"{unresolved_count} unresolved reference(s)."
            ),
            suggestion=(
                "Ensure all referenced USD layers exist and can be resolved."
            ),
            details={
                "unresolved_references": unresolved_count,
                "unresolved_count": unresolved_count,
            },
        )]

    return [CheckResult(
        check_id=USD_REFERENCES_RESOLVE,
        label="USD References Resolve",
        category="Dependencies",
        status=CheckStatus.PASSED,
        severity=runtime_context.default_severity,
        message="All USD references resolve successfully.",
        details={"unresolved_count": 0},
    )]


def check_payloads_resolve(context, runtime_context):
    unresolved_count = context.composition.unresolved_payloads

    if unresolved_count:
        return [CheckResult(
            check_id=USD_PAYLOADS_RESOLVE,
            label="USD Payloads Resolve",
            category="Dependencies",
            status=CheckStatus.FAILED,
            severity=runtime_context.default_severity,
            message=(
                f"The stage contains "
                f"{unresolved_count} unresolved payload(s)."
            ),
            suggestion=(
                "Ensure all payload USD layers exist and can be resolved."
            ),
            details={
                "unresolved_payloads": unresolved_count,
                "unresolved_count": unresolved_count,
            },
        )]

    return [CheckResult(
        check_id=USD_PAYLOADS_RESOLVE,
        label="USD Payloads Resolve",
        category="Dependencies",
        status=CheckStatus.PASSED,
        severity=runtime_context.default_severity,
        message="All USD payloads resolve successfully.",
        details={"unresolved_count": 0},
    )]