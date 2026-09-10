from pathlib import Path

from validation import CheckStatus, PublishChecker


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def get_result(report, check_id):
    return next(
        result
        for result in report.results
        if result.check_id == check_id
    )


def test_references_fail_to_resolve():
    source_path = FIXTURES_DIR / "invalid_dependencies.usda"

    report = PublishChecker().check(source_path)

    result = get_result(
        report,
        "USD_REFERENCES_RESOLVE",
    )

    assert result.status is CheckStatus.FAILED


def test_payloads_fail_to_resolve():
    source_path = FIXTURES_DIR / "invalid_dependencies.usda"

    report = PublishChecker().check(source_path)

    result = get_result(
        report,
        "USD_PAYLOADS_RESOLVE",
    )

    assert result.status is CheckStatus.FAILED


def test_dependencies_fail_to_resolve():
    source_path = FIXTURES_DIR / "invalid_dependencies.usda"

    report = PublishChecker().check(source_path)

    result = get_result(
        report,
        "USD_DEPENDENCIES_RESOLVE",
    )

    assert result.status is CheckStatus.FAILED