# validation/__init__.py

from .enums import CheckStatus, Severity
from .models import CheckDefinition, CheckResult, CheckTargetResult, ValidationSummary
from .publish_report import PublishReport
from .registry import ValidationRegistry


__all__ = [
    "CheckDefinition",
    "CheckResult",
    "CheckStatus",
    "CheckTargetResult",
    "PublishChecker",
    "PublishReport",
    "Severity",
    "ValidationRegistry",
    "ValidationSummary",
]


def __getattr__(name):
    if name == "PublishChecker":
        from .publish_checker import PublishChecker

        return PublishChecker

    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}"
    )