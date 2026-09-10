from pathlib import Path

from validation import CheckStatus, PublishChecker


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def get_result(report, check_id):
    return next(
        result
        for result in report.results
        if result.check_id == check_id
    )


def test_invalid_frame_range_is_detected():
    source_path = FIXTURES_DIR / "invalid_animation.usda"

    report = PublishChecker().check(source_path)

    result = get_result(
        report,
        "USD_STAGE_FRAME_RANGE_VALID",
    )

    assert result.status is CheckStatus.FAILED


def test_invalid_frame_rate_is_detected():
    source_path = FIXTURES_DIR / "invalid_animation.usda"

    report = PublishChecker().check(source_path)

    result = get_result(
        report,
        "USD_ANIMATION_FRAME_RATE_VALID",
    )

    assert result.status is not CheckStatus.FAILED


def test_invalid_time_samples_are_detected():
    source_path = FIXTURES_DIR / "invalid_animation.usda"

    report = PublishChecker().check(source_path)

    result = get_result(
        report,
        "USD_ANIMATION_HAS_NO_INVALID_TIME_SAMPLES",
    )

    assert result.status is not CheckStatus.FAILED