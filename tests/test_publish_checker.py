# tests/test_publish_checker.py

from pathlib import Path

from validation import CheckStatus, PublishChecker


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_valid_stage_opens():
    source_path = FIXTURES_DIR / "valid_stage.usda"
    report = PublishChecker().check(source_path)

    assert report.stage_opened
    assert report.publish_passed
    assert report.root_layer
    assert report.stage_health is not None
    assert len(report.results) == 1
    assert report.results[0].check_id == "USD_STAGE_CAN_OPEN"
    assert report.results[0].status is CheckStatus.PASSED


def test_missing_stage_fails():
    source_path = FIXTURES_DIR / "does_not_exist.usda"
    report = PublishChecker().check(source_path)

    assert not report.stage_opened
    assert not report.publish_passed
    assert report.stage_health is None
    assert len(report.results) == 1
    assert report.results[0].check_id == "USD_STAGE_CAN_OPEN"
    assert report.results[0].status is CheckStatus.FAILED