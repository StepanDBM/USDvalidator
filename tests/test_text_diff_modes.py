from s_usd_core.comparison.source_preflight import DiffMode
from s_usd_core.comparison.text_diff import (
    SUMMARY_CONTEXT_LINES,
    build_side_by_side_diff,
)


def _write(path, lines):
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_full_diff_retains_all_changed_rows(tmp_path):
    previous = tmp_path / "previous.usda"
    current = tmp_path / "current.usda"
    _write(previous, [f"old {index}" for index in range(100)])
    _write(current, [f"new {index}" for index in range(100)])

    rows = build_side_by_side_diff(previous, current, DiffMode.FULL)

    assert len(rows) == 100
    assert not any("omitted by Summary Diff" in row.old_text for row in rows)


def test_summary_diff_discards_middle_of_large_changed_region(tmp_path):
    previous = tmp_path / "previous.usda"
    current = tmp_path / "current.usda"
    _write(previous, [f"old {index}" for index in range(100)])
    _write(current, [f"new {index}" for index in range(100)])

    rows = build_side_by_side_diff(previous, current, DiffMode.SUMMARY)

    assert len(rows) == SUMMARY_CONTEXT_LINES * 2 + 1

    omitted = rows[SUMMARY_CONTEXT_LINES]

    assert omitted.kind == "OMITTED"
    assert omitted.omitted_old == 94
    assert omitted.omitted_new == 94
    assert "94 previous lines omitted" in omitted.old_text
    assert "94 current lines omitted" in omitted.new_text
    assert "old 50" not in {row.old_text for row in rows}
    assert "new 50" not in {row.new_text for row in rows}


def test_summary_diff_discards_middle_of_large_unchanged_region(tmp_path):
    previous = tmp_path / "previous.usda"
    current = tmp_path / "current.usda"
    lines = [f"same {index}" for index in range(100)]
    _write(previous, lines)
    _write(current, lines)

    rows = build_side_by_side_diff(previous, current, DiffMode.SUMMARY)

    assert len(rows) == SUMMARY_CONTEXT_LINES * 2 + 1

    omitted = rows[SUMMARY_CONTEXT_LINES]

    assert omitted.kind == "OMITTED"
    assert omitted.omitted_old == 94
    assert omitted.omitted_new == 94
    assert "94 unchanged lines omitted" in omitted.old_text
    assert "94 unchanged lines omitted" in omitted.new_text
    assert "same 50" not in {row.old_text for row in rows}
    assert "same 50" not in {row.new_text for row in rows}


def test_skip_diff_returns_no_rows(tmp_path):
    previous = tmp_path / "previous.usda"
    current = tmp_path / "current.usda"
    _write(previous, ["old"])
    _write(current, ["new"])

    assert build_side_by_side_diff(previous, current, DiffMode.SKIP) == ()
