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


def test_profile_editor_controls_and_rows_have_tooltips():
    run_qt("""
        from PySide6.QtWidgets import QApplication
        from s_usd_core.rules import build_registry
        from s_usd_core.validation.profile_loader import ProfileLoader
        from s_usd_desktop.ui.widgets.profile_editor import ProfileEditor

        application = QApplication([])
        editor = ProfileEditor(
            ProfileLoader("s_usd_core/validation/profiles.json"), build_registry()
        )
        controls = {
            "new": editor.new_button, "delete": editor.delete_button,
            "profiles": editor.profile_list, "name": editor.name_edit,
            "description": editor.description_edit,
            "reset": editor.reset_button, "save": editor.save_button,
            "category": editor.category_combo, "tag": editor.tag_combo,
            "search": editor.search_edit, "add_checks": editor.add_checks_button,
            "remove_checks": editor.remove_checks_button,
            "checks": editor.check_tree,
            "create_override": editor.create_override_button,
            "edit_override": editor.edit_override_button,
            "toggle_override": editor.toggle_override_button,
            "remove_override": editor.remove_override_button,
            "overrides": editor.override_tree
        }
        for name, control in controls.items():
            assert len(control.toolTip()) >= 20, f"{name}: {control.toolTip()!r}"
        assert editor.profile_list.count() > 0
        assert len(editor.profile_list.item(0).toolTip()) >= 20
        category = editor.check_tree.topLevelItem(0)
        if category and category.childCount():
            assert len(category.child(0).toolTip(0)) >= 20
        editor.close()
        application.processEvents()
    """)


def test_validation_result_rows_have_contextual_tooltips():
    run_qt("""
        from types import SimpleNamespace
        from PySide6.QtWidgets import QApplication
        from s_usd_desktop.ui.widgets.results_browser.results_tree import ResultsTree

        application = QApplication([])
        tree = ResultsTree()
        result = SimpleNamespace(
            check_id="USD_TEST_CHECK", label="Test Check", category="Testing",
            status=SimpleNamespace(value="FAILED"),
            severity=SimpleNamespace(value="ERROR"), location="/World/Test",
            layer="root.usda", message="The test condition failed.",
            suggestion="Repair the test condition.", details={"observed": False}
        )
        tree.set_results((result,))
        item = tree.topLevelItem(0).child(0)
        assert "USD_TEST_CHECK" in item.toolTip(0)
        assert "FAILED" in item.toolTip(0)
        assert "/World/Test" in item.toolTip(0)
        assert all(len(item.toolTip(column)) >= 20 for column in range(tree.columnCount()))
        tree.close()
        application.processEvents()
    """)
