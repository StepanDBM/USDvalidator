from validation.enums import CheckStatus
from validation.models import CheckResult


def result(
    check_id,
    label,
    category,
    runtime_context,
    passed,
    message,
    location="",
    details=None,
    suggestion="",
):
    return [CheckResult(
        check_id=check_id,
        label=label,
        category=category,
        status=CheckStatus.PASSED if passed else CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message=message,
        location=location,
        details=details or {},
        suggestion=suggestion,
    )]


def csv_values(value):
    return tuple(item.strip() for item in value.split(",") if item.strip())
