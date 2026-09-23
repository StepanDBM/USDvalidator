import os
import subprocess
import sys
import textwrap

import pytest

pytest.importorskip("PySide6")


def run_qt_test(code):
    environment = os.environ.copy()
    environment["QT_QPA_PLATFORM"] = "offscreen"
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code)],
        cwd=os.getcwd(),
        env=environment,
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, (
        f"Qt subprocess failed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


def test_upload_dialog_can_preselect_root_layer():
    run_qt_test("""
        from PySide6.QtWidgets import QApplication

        from s_usd_desktop.ui.storage.dialogs import UploadFileDialog

        application = QApplication([])
        dialog = UploadFileDialog(initial_role="root_layer")

        assert dialog.role.currentText() == "root_layer"

        dialog.close()
        application.processEvents()
    """)


def test_compact_menu_button_exposes_actions():
    run_qt_test("""
        from PySide6.QtWidgets import QApplication

        from s_usd_desktop.ui.storage.workspace import StorageWorkspace

        application = QApplication([])
        calls = []

        button = StorageWorkspace._menu_button("New", (
            ("Project...", lambda: calls.append("project")),
            ("Version...", lambda: calls.append("version"))
        ))

        assert button.text() == "New"
        assert [action.text() for action in button.menu().actions()] == [
            "Project...",
            "Version..."
        ]

        button.menu().actions()[1].trigger()
        assert calls == ["version"]

        button.close()
        application.processEvents()
    """)