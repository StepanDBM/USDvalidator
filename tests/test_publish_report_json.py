import json
from pathlib import Path

from validation import PublishChecker


def test_publish_report_serializes_to_stable_json():
    checker = PublishChecker()
    report = checker.check("tests/fixtures/valid_stage.usda")

    data = report.to_dict()

    expected_path = Path("tests/fixtures/valid_stage.usda").resolve()

    assert data["schema_version"] == "1.0"
    assert data["source"]["path"] == str(expected_path).replace("\\", "/")
    assert data["source"]["stage_opened"] is True
    assert data["summary"]["total"] == len(report.results)
    assert data["summary"]["failed"] == 0
    assert data["summary"]["errors"] == 0
    assert isinstance(data["results"], list)
    assert len(data["results"]) == len(report.results)

    first_result = data["results"][0]

    assert isinstance(first_result["check_id"], str)
    assert isinstance(first_result["status"], str)
    assert isinstance(first_result["severity"], str)
    assert isinstance(first_result["details"], dict)

    json_text = report.to_json()
    parsed = json.loads(json_text)

    assert parsed == data


def test_publish_report_writes_json(tmp_path):
    checker = PublishChecker()
    report = checker.check("tests/fixtures/valid_stage.usda")

    output_path = tmp_path / "report.json"

    report.write_json(output_path)

    assert output_path.exists()

    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert data["schema_version"] == "1.0"
    assert data["source"]["stage_opened"] is True