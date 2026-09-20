from types import SimpleNamespace
import pytest
pxr = pytest.importorskip("pxr")
from pxr import Usd
from s_usd_core.validation.enums import CheckStatus, Severity
from s_usd_core.validation.models import CheckTargetResult
from s_usd_desktop.ui.widgets.usd_viewport.prim_finding_index import PrimFindingIndex

def result(location, status=CheckStatus.FAILED, targets=()):
    return SimpleNamespace(location=location, details={}, status=status, severity=Severity.ERROR, targets=targets)

def test_direct_property_and_descendant_results():
    stage = Usd.Stage.CreateInMemory()
    stage.DefinePrim("/World", "Xform")
    stage.DefinePrim("/World/Mesh", "Mesh")
    index = PrimFindingIndex(stage, [result("/World/Mesh.points"), result("/World/Mesh")])
    assert len(index.summary("/World/Mesh").direct) == 2
    assert len(index.summary("/World").descendants) == 2

def test_unresolved_result_is_stage_level():
    stage = Usd.Stage.CreateInMemory()
    finding = result("C:/missing/file.usda")
    index = PrimFindingIndex(stage, [finding])
    assert index.stage_results == [finding]


def test_explicit_targets_take_precedence_over_legacy_location():
    stage = Usd.Stage.CreateInMemory()
    stage.DefinePrim("/World", "Xform")
    stage.DefinePrim("/World/Good", "Mesh")
    stage.DefinePrim("/World/Bad", "Mesh")
    finding = result("/World", targets=(
        CheckTargetResult("/World/Good", status=CheckStatus.PASSED),
        CheckTargetResult("/World/Bad", "/World/Bad.points", CheckStatus.FAILED),
    ))
    index = PrimFindingIndex(stage, [finding])
    assert index.summary("/World").direct_count == 0
    assert index.summary("/World").descendant_count == 2
    assert index.summary("/World/Good").passed_count == 1
    assert index.summary("/World/Bad").failed_count == 1


def test_parent_summary_keeps_failed_target_severity():
    stage = Usd.Stage.CreateInMemory()
    stage.DefinePrim("/World", "Xform")
    stage.DefinePrim("/World/A", "Mesh")
    stage.DefinePrim("/World/B", "Mesh")
    finding = result("", targets=(
        CheckTargetResult("/World/A", status=CheckStatus.PASSED),
        CheckTargetResult("/World/B", status=CheckStatus.FAILED),
    ))
    summary = PrimFindingIndex(stage, [finding]).summary("/World")
    assert summary.total_count == 2
    assert summary.passed_count == 1
    assert summary.failed_count == 1
    assert summary.highest_severity_rank == 3
