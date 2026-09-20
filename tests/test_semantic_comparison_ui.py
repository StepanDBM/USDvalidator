import pytest

pytest.importorskip("PySide6")

from s_usd_core.comparison.models import ChangeImpact, ChangeKind, ComparisonResult, SemanticChange
from s_usd_desktop.ui.widgets.comparison_browser.semantic_toolbar import SemanticComparisonToolbar
from s_usd_desktop.ui.widgets.comparison_browser.semantic_tree import SemanticChangesTree


@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def _comparison():
    return ComparisonResult(
        "previous.usda",
        "current.usda",
        changes=[
            SemanticChange(
                "Transforms", "/World/NewProp", "Transform prim removed",
                ChangeKind.REMOVED, "Transform", None,
                domain="Transforms", impact=ChangeImpact.HIGH,
            ),
            SemanticChange(
                "Hierarchy", "/World/Body", "Prim removed (Mesh)",
                ChangeKind.REMOVED, "Mesh", None,
                domain="Hierarchy", impact=ChangeImpact.LOW,
            ),
            SemanticChange(
                "Validation", "USD_TEST", "Test regression",
                ChangeKind.REGRESSION, "PASSED", "FAILED",
                domain="Validation", impact=ChangeImpact.CRITICAL,
            ),
        ],
    )


def test_semantic_view_is_a_flat_list(app):
    tree = SemanticChangesTree()
    tree.set_comparison(_comparison())
    assert tree.topLevelItemCount() == 3
    assert all(tree.topLevelItem(index).childCount() == 0 for index in range(3))
    assert tree.topLevelItem(0).text(0) == "Validation"
    assert tree.topLevelItem(1).text(0) == "Transforms"
    assert tree.topLevelItem(1).text(1) == "/World/NewProp"


def test_domain_filter_reduces_visible_rows(app):
    tree = SemanticChangesTree()
    tree.set_comparison(_comparison(), filters={"domain": "Hierarchy"})
    assert tree.topLevelItemCount() == 1
    assert tree.topLevelItem(0).text(0) == "Hierarchy"


def test_impact_kind_and_regression_filters_work(app):
    tree = SemanticChangesTree()
    comparison = _comparison()
    tree.set_comparison(comparison, filters={"impact": "HIGH"})
    assert tree.topLevelItemCount() == 1
    tree.set_comparison(comparison, filters={"kind": "REMOVED"})
    assert tree.topLevelItemCount() == 2
    tree.set_comparison(comparison, filters={"regressions_only": True})
    assert tree.topLevelItemCount() == 1
    assert tree.topLevelItem(0).text(3) == "REGRESSION"


def test_toolbar_uses_stable_filter_values(app):
    toolbar = SemanticComparisonToolbar()
    toolbar.set_comparison(_comparison())
    toolbar.domain_combo.setCurrentIndex(toolbar.domain_combo.findData("Transforms"))
    toolbar.impact_combo.setCurrentIndex(toolbar.impact_combo.findData("HIGH"))
    assert toolbar.filters()["domain"] == "Transforms"
    assert toolbar.filters()["impact"] == "HIGH"
