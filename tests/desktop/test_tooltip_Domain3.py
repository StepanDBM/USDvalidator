import os
import subprocess
import sys
import textwrap

import pytest

pytest.importorskip("PySide6")


def run_qt(code):
    environment = os.environ.copy()
    environment["QT_QPA_PLATFORM"] = "offscreen"
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code)], cwd=os.getcwd(),
        env=environment, capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, (
        f"Qt subprocess failed.\nstdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


def test_comparison_controls_have_explanatory_tooltips():
    run_qt("""
        from PySide6.QtWidgets import QApplication
        from s_usd_core.validation.profile_loader import ProfileLoader
        from s_usd_desktop.ui.widgets.comparison_browser.comparison_view import ComparisonView

        application = QApplication([])
        view = ComparisonView(ProfileLoader("s_usd_core/validation/profiles.json"))
        controls = {
            "previous_source": view.previous_edit,
            "previous_browse": view.previous_button,
            "current_source": view.current_edit,
            "current_browse": view.current_button,
            "profile": view.profile_combo,
            "swap": view.swap_button,
            "compare": view.compare_button,
            "show_unchanged": view.show_unchanged,
            "progress": view.progress_bar,
            "cancel": view.cancel_button,
            "impact": view.semantic_toolbar.impact_combo,
            "domain": view.semantic_toolbar.domain_combo,
            "kind": view.semantic_toolbar.kind_combo,
            "regressions": view.semantic_toolbar.regressions_only,
            "semantic_tree": view.semantic_tree,
            "change_details": view.change_details,
            "diff_table": view.diff_view.table,
            "diff_previous": view.diff_view.toolbar.previous_button,
            "diff_next": view.diff_view.toolbar.next_button,
            "changes_only": view.diff_view.toolbar.changes_only_check,
            "collapse": view.diff_view.toolbar.collapse_all_button,
            "expand": view.diff_view.toolbar.expand_all_button
        }
        for name, control in controls.items():
            assert len(control.toolTip()) >= 20, f"{name}: {control.toolTip()!r}"
        view.close()
        application.processEvents()
    """)


def test_semantic_and_source_diff_rows_have_contextual_tooltips():
    run_qt("""
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication
        from s_usd_core.comparison.models import (
            ChangeImpact, ChangeKind, ComparisonResult, SemanticChange
        )
        from s_usd_core.comparison.text_diff import DiffLine
        from s_usd_desktop.ui.widgets.comparison_browser.diff_view import SideBySideDiffModel
        from s_usd_desktop.ui.widgets.comparison_browser.semantic_tree import SemanticChangesTree

        application = QApplication([])
        comparison = ComparisonResult("previous.usda", "current.usda")
        comparison.changes.append(SemanticChange(
            "Transforms", "/World/Asset", "Transform scale values",
            ChangeKind.CHANGED, (1, 1, 1), (2, 2, 2),
            domain="Transforms", property_path="scale_values",
            impact=ChangeImpact.HIGH,
            why_it_matters="Scale changes can alter size and handedness."
        ))
        tree = SemanticChangesTree()
        tree.set_comparison(comparison)
        item = tree.topLevelItem(0)
        assert "Transforms" in item.toolTip(0)
        assert "HIGH" in item.toolTip(0)
        assert "Scale changes" in item.toolTip(0)
        assert all(len(item.toolTip(column)) >= 20 for column in range(tree.columnCount()))

        model = SideBySideDiffModel()
        model.set_rows((DiffLine(4, 4, "old", "new", "CHANGED"),))
        tooltip = model.data(model.index(0, 2), Qt.ItemDataRole.ToolTipRole)
        assert "CHANGED" in tooltip
        assert "Previous line: 4" in tooltip
        assert "Current line: 4" in tooltip
        tree.close()
        application.processEvents()
    """)
