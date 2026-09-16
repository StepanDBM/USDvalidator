from types import SimpleNamespace

from validation.enums import CheckStatus, Severity
from validation.models import CheckResult, CheckTargetResult
from validation.publish_report import PublishReport



def check_result(**kwargs):
    values = dict(check_id="test", label="Test", category="Test", status=CheckStatus.PASSED, severity=Severity.ERROR, message="ok")
    values.update(kwargs)
    return CheckResult(**values)


def test_check_target_result_is_immutable_and_defaults_to_passed():
    target = CheckTargetResult("/World/Mesh")
    assert target.status is CheckStatus.PASSED
    try:
        target.prim_path = "/Other"
    except Exception:
        pass
    assert target.prim_path == "/World/Mesh"


def test_check_result_targets_default_to_empty_tuple():
    assert check_result().targets == ()



def test_report_target_round_trip_and_legacy_default():
    target = CheckTargetResult("/World/Mesh", "/World/Mesh.points", CheckStatus.FAILED, 0, "> 0", "No points")
    report = PublishReport("scene.usda", True, "scene.usda", results=[check_result(status=CheckStatus.FAILED, targets=(target,))])
    restored = PublishReport.from_dict(report.to_dict())
    assert restored.results[0].targets == (target,)
    legacy = report.to_dict()
    legacy["results"][0].pop("targets")
    assert PublishReport.from_dict(legacy).results[0].targets == ()
