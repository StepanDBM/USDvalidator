from pathlib import Path

from validation import CheckStatus, PublishChecker


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_default_prim_is_validated_as_authored():
    source_path = FIXTURES_DIR / "valid_stage.usda"

    report = PublishChecker().check(source_path)

    result = next(
        result
        for result in report.results
        if result.check_id == "USD_DEFAULT_PRIM_AUTHORED"
    )

    assert result.status is CheckStatus.PASSED
    assert result.location == "/World"

def test_missing_default_prim_fails():
    source_path = FIXTURES_DIR / "no_default_prim.usda"

    report = PublishChecker().check(source_path)

    result = next(
        result
        for result in report.results
        if result.check_id == "USD_DEFAULT_PRIM_AUTHORED"
    )

    assert result.status is CheckStatus.FAILED
    assert result.severity.value == "ERROR"

def test_invalid_default_prim_is_detected():
    source_path = FIXTURES_DIR / "invalid_default_prim.usda"
    report = PublishChecker().check(source_path)

    result = next(
        result
        for result in report.results
        if result.check_id == "USD_DEFAULT_PRIM_VALID"
    )

    assert result.status is CheckStatus.FAILED
    assert result.location == "/DoesNotExist"