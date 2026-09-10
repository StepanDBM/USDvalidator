# tests/test_summary.py

from validation import CheckResult, CheckStatus, Severity, ValidationSummary


def make_result(status, severity):
    return CheckResult(
        check_id="USD_TEST",
        label="Test",
        category="Tests",
        status=status,
        severity=severity,
        message="Test result"
    )


def test_summary_counts_status_and_issue_severity():
    results = [
        make_result(CheckStatus.PASSED, Severity.INFO),
        make_result(CheckStatus.FAILED, Severity.WARNING),
        make_result(CheckStatus.ERROR, Severity.ERROR),
        make_result(CheckStatus.SKIPPED, Severity.INFO)
    ]
    summary = ValidationSummary.from_results(results)
    assert summary.total == 4
    assert summary.passed == 1
    assert summary.failed == 1
    assert summary.skipped == 1
    assert summary.internal_errors == 1
    assert summary.errors == 1
    assert summary.warnings == 1
