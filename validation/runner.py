import traceback

from .enums import CheckStatus, Severity
from .models import CheckResult
from .runtime_context import CheckRuntimeContext


def execute_checks(definitions, targets):
    results = []

    for definition in definitions:
        compatible_targets = [
            target
            for target in targets
            if isinstance(target, definition.target_type)
        ]

        if not compatible_targets:
            results.append(CheckResult(
                check_id=definition.check_id,
                label=definition.label,
                category=definition.category,
                status=CheckStatus.SKIPPED,
                severity=Severity.INFO,
                message=(
                    f"No {definition.target_type.__name__} target "
                    "was available."
                ),
            ))
            continue

        runtime_context = CheckRuntimeContext(
            check_id=definition.check_id,
            default_severity=definition.default_severity,
        )

        for target in compatible_targets:
            try:
                check_results = definition.func(
                    target,
                    runtime_context,
                ) or []

                results.extend(check_results)

            except Exception as exc:
                results.append(CheckResult(
                    check_id=definition.check_id,
                    label=definition.label,
                    category=definition.category,
                    status=CheckStatus.ERROR,
                    severity=Severity.ERROR,
                    message=f"Check failed internally: {exc}",
                    details={
                        "traceback": traceback.format_exc(),
                    },
                ))

    return results