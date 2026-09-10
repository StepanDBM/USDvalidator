
# validation/models.py
from dataclasses import dataclass, field
from typing import Any, Callable

from .enums import CheckStatus, Severity

CheckFunction = Callable[[Any, Any], list["CheckResult"]]


@dataclass(frozen=True)
class CheckDefinition:
    check_id: str
    label: str
    func: CheckFunction
    target_type: type
    category: str
    phase: str
    default_severity: Severity
    tags: tuple[str, ...] = ()
    enabled: bool = True


@dataclass
class CheckResult:
    check_id: str
    label: str
    category: str
    status: CheckStatus
    severity: Severity
    message: str
    location: str = ""
    layer: str = ""
    suggestion: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationSummary:
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    internal_errors: int = 0
    errors: int = 0
    warnings: int = 0
    info: int = 0

    @classmethod
    def from_results(cls, results):
        summary = cls(total=len(results))
        for result in results:
            if result.status is CheckStatus.PASSED:
                summary.passed += 1
            elif result.status is CheckStatus.FAILED:
                summary.failed += 1
            elif result.status is CheckStatus.SKIPPED:
                summary.skipped += 1
            elif result.status is CheckStatus.ERROR:
                summary.internal_errors += 1

            if result.status in {CheckStatus.FAILED, CheckStatus.ERROR}:
                if result.severity is Severity.ERROR:
                    summary.errors += 1
                elif result.severity is Severity.WARNING:
                    summary.warnings += 1
                elif result.severity is Severity.INFO:
                    summary.info += 1
        return summary
