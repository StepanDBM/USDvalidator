from types import SimpleNamespace

import pytest

pytest.importorskip("PySide6")
pytest.importorskip("pxr")
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from pxr import Sdf, Usd

from ui.widgets.usd_viewport.stage_outliner import StageOutliner
from validation.enums import CheckStatus, Severity
from validation.models import CheckTargetResult


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def stage_with_filters():
    stage = Usd.Stage.CreateInMemory()
    stage.DefinePrim("/World", "Xform")
    stage.DefinePrim("/World/StaticMesh", "Mesh")
    animated = stage.DefinePrim("/World/AnimatedMesh", "Mesh")
    animated.CreateAttribute("animatedValue", Sdf.ValueTypeNames.Double).Set(1.0, 1.0)
    stage.DefinePrim("/World/Camera", "Camera")
    return stage


def finding(*targets):
    return SimpleNamespace(location="", details={}, status=CheckStatus.FAILED, severity=Severity.ERROR, targets=targets)


def visible_paths(outliner):
    return {path for path in outliner.model.items if outliner.proxy.mapFromSource(outliner.model.index_for_path(path)).isValid()}


def test_search_and_type_filters_preserve_ancestor_context(qapp):
    outliner = StageOutliner()
    outliner.set_stage(stage_with_filters())
    outliner.filter_edit.setText("StaticMesh")
    assert visible_paths(outliner) == {"/World", "/World/StaticMesh"}
    outliner.filter_edit.clear()
    outliner.type_actions["Mesh"].setChecked(False)
    paths = visible_paths(outliner)
    assert "/World/StaticMesh" not in paths
    assert "/World/Camera" in paths


def test_validation_findings_and_status_filters(qapp):
    outliner = StageOutliner()
    outliner.set_stage(stage_with_filters())
    outliner.set_validation_results([finding(
        CheckTargetResult("/World/StaticMesh", status=CheckStatus.PASSED),
        CheckTargetResult("/World/AnimatedMesh", status=CheckStatus.FAILED),
    )])
    outliner.findings_only.setChecked(True)
    assert visible_paths(outliner) == {"/World", "/World/StaticMesh", "/World/AnimatedMesh"}
    outliner.status_actions["FAILED"].setChecked(True)
    assert visible_paths(outliner) == {"/World", "/World/AnimatedMesh"}


def test_animated_only_filter_and_expansion_restore(qapp):
    outliner = StageOutliner()
    outliner.set_stage(stage_with_filters())
    world = outliner.proxy.mapFromSource(outliner.model.index_for_path("/World"))
    outliner.tree.setExpanded(world, False)
    outliner.animated_only.setChecked(True)
    assert visible_paths(outliner) == {"/World", "/World/AnimatedMesh"}
    outliner.animated_only.setChecked(False)
    world = outliner.proxy.mapFromSource(outliner.model.index_for_path("/World"))
    assert not outliner.tree.isExpanded(world)


def test_filtering_preserves_selection(qapp):
    outliner = StageOutliner()
    outliner.set_stage(stage_with_filters())
    outliner.select_path("/World/StaticMesh")
    outliner.filter_edit.setText("Camera")
    outliner.filter_edit.clear()
    assert "/World/StaticMesh" in outliner.selected_paths()


def test_info_filter_keeps_nonmatching_hierarchy_headers(qapp):
    stage = Usd.Stage.CreateInMemory()
    stage.DefinePrim("/Kitchen", "Xform")
    stage.DefinePrim("/Kitchen/Props", "Scope")
    stage.DefinePrim("/Kitchen/Props/Table", "Xform")
    stage.DefinePrim("/Kitchen/Props/Table/Plate", "Mesh")
    outliner = StageOutliner()
    outliner.set_stage(stage)
    info_result = SimpleNamespace(
        location="", details={}, status=CheckStatus.PASSED, severity=Severity.INFO,
        targets=(CheckTargetResult("/Kitchen/Props/Table/Plate", status=CheckStatus.PASSED),),
    )
    outliner.set_validation_results([info_result])
    outliner.status_actions["INFO"].setChecked(True)
    assert visible_paths(outliner) == {
        "/Kitchen", "/Kitchen/Props", "/Kitchen/Props/Table", "/Kitchen/Props/Table/Plate",
    }
    kitchen = outliner.proxy.mapFromSource(outliner.model.index_for_path("/Kitchen"))
    plate = outliner.proxy.mapFromSource(outliner.model.index_for_path("/Kitchen/Props/Table/Plate"))
    assert kitchen.data(outliner.proxy.MATCH_ROLE) == outliner.proxy.ANCESTOR_CONTEXT
    assert plate.data(outliner.proxy.MATCH_ROLE) == outliner.proxy.DIRECT_MATCH
    assert "Shown because 1 descendant matches" in kitchen.data(Qt.ItemDataRole.ToolTipRole)
