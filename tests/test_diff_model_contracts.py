import pytest
pytest.importorskip("PySide6")

from PySide6.QtCore import Qt

from s_usd_core.comparison.source_preflight import DiffMode
from s_usd_core.comparison.text_diff import DiffLine, SourceDiffResult
from s_usd_desktop.ui.widgets.comparison_browser.diff_view import (
    MAX_DISPLAY_LINE_LENGTH,
    MAX_TOOLTIP_LINE_LENGTH,
    SideBySideDiffModel,
)


def test_omitted_rows_are_not_changes_or_collapsible():
    rows = (
        DiffLine(1, 1, "start", "start", "UNCHANGED"),
        DiffLine(None, None, "94 omitted", "94 omitted", "OMITTED", 94, 94),
        DiffLine(100, 100, "end", "end", "UNCHANGED"),
    )
    model = SideBySideDiffModel()
    model.set_rows(rows)
    assert model.change_regions == ()
    assert model.sections == {}
    model.expand_all()
    assert model.rowCount() == 3


def test_large_display_and_tooltip_are_bounded():
    text = "x" * (MAX_DISPLAY_LINE_LENGTH + 500)
    model = SideBySideDiffModel()
    model.set_rows((DiffLine(1, 1, text, text, "CHANGED"),))
    display = model.data(model.index(0, 1), Qt.ItemDataRole.DisplayRole)
    tooltip = model.data(model.index(0, 1), Qt.ItemDataRole.ToolTipRole)
    assert len(display) < len(text)
    assert len(tooltip) < len(display)
    assert "500 characters hidden" in display
    assert model.rows[0].old_text == text


def test_full_expand_all_exposes_generated_rows():
    rows = tuple(DiffLine(i + 1, i + 1, str(i), str(i), "CHANGED") for i in range(30))
    model = SideBySideDiffModel()
    model.set_rows(rows)
    assert model.rowCount() == 2
    model.expand_all()
    assert model.rowCount() == 30


def test_summary_expand_all_cannot_restore_omitted_rows():
    rows = (
        DiffLine(1, 1, "first", "first", "CHANGED"),
        DiffLine(None, None, "94 omitted", "94 omitted", "OMITTED", 94, 94),
        DiffLine(100, 100, "last", "last", "CHANGED"),
    )
    result = SourceDiffResult(DiffMode.SUMMARY, rows, 100, 100, 94, 94)
    model = SideBySideDiffModel()
    model.set_rows(result.rows)
    model.expand_all()
    assert model.rowCount() == 3
    assert sum(row.omitted_old for row in model.rows) == 94
