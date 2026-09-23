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
        [sys.executable, "-c", textwrap.dedent(code)],
        cwd=os.getcwd(), env=environment,
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, (
        f"Qt subprocess failed.\nstdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


def test_validation_controls_have_explanatory_tooltips():
    run_qt("""
        from PySide6.QtWidgets import QApplication
        from s_usd_core.validation.profile_loader import ProfileLoader
        from s_usd_desktop.ui.widgets.validation_view import ValidationView

        application = QApplication([])
        view = ValidationView(ProfileLoader("s_usd_core/validation/profiles.json"))

        controls = (
            view.validate_button,
            view.cancel_button,
            view.progress_bar,
            view.recursive_checkbox,
            view.include_edit,
            view.exclude_edit,
            view.worker_count_spin,
            view.output_edit,
            view.output_button,
            view.batch_report_checkbox,
            view.per_file_checkbox,
            view.manifest_checkbox,
            view.source_selector.browse_button,
            view.profile_selector.combo,
            view.results_view.filter_bar.status_combo,
            view.results_view.filter_bar.severity_combo,
            view.results_view.filter_bar.category_combo,
            view.results_view.filter_bar.search_edit,
            view.results_view.results_tree,
            view.results_view.result_details
        )
        assert all(len(control.toolTip()) >= 20 for control in controls)
        view.close()
        application.processEvents()
    """)


def test_connection_controls_have_explanatory_tooltips():
    run_qt("""
        from PySide6.QtWidgets import QApplication
        from s_usd_desktop.services.desktop_settings import ConnectionPreferences
        from s_usd_desktop.ui.dialogs.connection_settings import ConnectionSettingsDialog
        from s_usd_desktop.ui.widgets.connection.indicator import ConnectionIndicator

        application = QApplication([])
        dialog = ConnectionSettingsDialog(ConnectionPreferences())
        indicator = ConnectionIndicator()

        controls = (
            ("base_url", dialog.base_url),
            ("connect_timeout", dialog.connect_timeout),
            ("request_timeout", dialog.request_timeout),
            ("auto_connect", dialog.auto_connect),
            ("indicator_dot", indicator.dot),
            ("indicator_label", indicator.label),
            ("retry_button", indicator.retry_button),
            ("settings_button", indicator.settings_button)
        )

        for name, control in controls:
            assert len(control.toolTip()) >= 20, (
                f"{name} has a missing or insufficient tooltip: "
                f"{control.toolTip()!r}"
            )
            
        from s_usd_desktop.services.connection_service import ConnectionState

        indicator.set_state(
            ConnectionState.ERROR,
            error="Connection refused by 127.0.0.1:8000."
        )

        assert "Connection refused" in indicator.label.toolTip()
        assert "service" in indicator.label.toolTip().lower()
        dialog.close()
        indicator.close()
        application.processEvents()
    """)

