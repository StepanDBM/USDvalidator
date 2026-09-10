# validation/demo.py

from dataclasses import dataclass

from .enums import CheckStatus, Severity
from .models import CheckDefinition, CheckResult, ValidationSummary
from .registry import ValidationRegistry
from .runner import execute_checks


@dataclass
class DemoContext:
    name: str
    valid: bool


def check_demo(context, runtime_context):
    status = CheckStatus.PASSED if context.valid else CheckStatus.FAILED
    message = "Demo context is valid." if context.valid else "Demo context is invalid."
    return [CheckResult(
        check_id="USD_DEMO_VALID",
        label="Demo Validation",
        category="Foundation",
        status=status,
        severity=Severity.ERROR,
        message=message,
        location=context.name
    )]


def run_demo():
    registry = ValidationRegistry()
    registry.register(CheckDefinition(
        check_id="USD_DEMO_VALID",
        label="Demo Validation",
        func=check_demo,
        target_type=DemoContext,
        category="Foundation",
        phase="open",
        default_severity=Severity.ERROR
    ))

    results = execute_checks(registry, [DemoContext("DemoStage", True)])
    summary = ValidationSummary.from_results(results)

    print("USDvalidator foundation is running.")
    for result in results:
        print(f"[{result.status.value}] {result.check_id}: {result.message}")
    print(f"Total: {summary.total} | Passed: {summary.passed} | Failed: {summary.failed}")
