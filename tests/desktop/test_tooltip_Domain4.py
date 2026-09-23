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
    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"


def test_viewport_controls_have_explanatory_tooltips():
    run_qt("""
        from PySide6.QtWidgets import QApplication
        from s_usd_desktop.ui.widgets.usd_viewport.viewport_toolbar import ViewportToolbar
        from s_usd_desktop.ui.widgets.usd_viewport.timeline import TimelineWidget
        from s_usd_desktop.ui.widgets.usd_viewport.viewport_tools import ViewportTools
        from s_usd_desktop.ui.widgets.usd_viewport.stage_outliner import StageOutliner
        from s_usd_desktop.ui.widgets.usd_viewport.inspector.property_table import PropertyTable
        from s_usd_desktop.ui.widgets.usd_viewport.inspector.context_tabs import ContextTabs

        application = QApplication([])
        toolbar, timeline, tools = ViewportToolbar(), TimelineWidget(), ViewportTools()
        outliner, properties, context = StageOutliner(), PropertyTable(), ContextTabs()
        controls = (
            toolbar.source_edit, toolbar.browse_button, toolbar.open_button,
            timeline.to_start, timeline.previous_sample, timeline.previous_frame,
            timeline.play, timeline.next_frame, timeline.next_sample, timeline.to_end,
            timeline.slider, timeline.start_box, timeline.time_box, timeline.end_box,
            tools.camera_combo, tools.renderer_combo, tools.aov_combo,
            tools.draw_mode_combo, tools.complexity_combo, tools.background_combo,
            tools.auto_clip, tools.highlight, tools.highlight_color,
            outliner.filter_edit, outliner.tree, outliner.validation_toggle,
            outliner.validation_refresh, outliner.type_filter, outliner.status_filter,
            outliner.findings_only, outliner.animated_only, outliner.display_mode,
            outliner.comparison_filter, properties.search, properties.table, context
        )
        assert all(len(control.toolTip()) >= 20 for control in controls)
        assert all(len(context.tabToolTip(index)) >= 20 for index in range(context.count()))
        application.processEvents()
    """)


def test_viewport_property_rows_have_contextual_tooltips():
    run_qt("""
        from PySide6.QtWidgets import QApplication
        from s_usd_desktop.ui.widgets.usd_viewport.inspector.property_table import PropertyRow, PropertyTable

        application = QApplication([])
        table = PropertyTable()
        table._rows = [PropertyRow("A", "visibility", "inherited", "inherited")]
        table._rebuild()
        item = table.table.item(0, 1)
        assert "visibility" in item.toolTip()
        assert "inherited" in item.toolTip()
        application.processEvents()
    """)
