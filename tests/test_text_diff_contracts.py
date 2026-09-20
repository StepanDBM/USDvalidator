import pytest

from s_usd_core.comparison.progress import CancellationToken, ComparisonCancelled, ProgressUpdate
from s_usd_core.comparison.source_preflight import DiffMode
from s_usd_core.comparison.text_diff import SUMMARY_CONTEXT_LINES, build_source_diff


def _write(path, lines):
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _pair(tmp_path, old_lines, new_lines, suffix=".usda"):
    previous = tmp_path / f"previous{suffix}"
    current = tmp_path / f"current{suffix}"
    _write(previous, old_lines)
    _write(current, new_lines)
    return previous, current


@pytest.mark.parametrize("mode", (DiffMode.FULL, DiffMode.SUMMARY, DiffMode.SKIP))
def test_diff_modes_are_reported(tmp_path, mode):
    previous, current = _pair(tmp_path, ["old"], ["new"])
    assert build_source_diff(previous, current, mode).mode is mode


def test_full_retains_large_replacement(tmp_path):
    previous, current = _pair(
        tmp_path,
        [f"old {index}" for index in range(100)],
        [f"new {index}" for index in range(100)],
    )
    result = build_source_diff(previous, current, DiffMode.FULL)
    assert len(result.rows) == 100
    assert result.omitted_total == 0
    assert all(row.kind != "OMITTED" for row in result.rows)


@pytest.mark.parametrize(
    "old_lines,new_lines,expected_old,expected_new",
    (
        ([f"same {i}" for i in range(100)], [f"same {i}" for i in range(100)], 94, 94),
        ([f"old {i}" for i in range(100)], [f"new {i}" for i in range(100)], 94, 94),
        ([f"old {i}" for i in range(100)], [], 94, 0),
        ([], [f"new {i}" for i in range(100)], 0, 94),
        ([f"old {i}" for i in range(100)], [f"new {i}" for i in range(200)], 94, 194),
    ),
)
def test_summary_permanently_omits_large_regions(
    tmp_path, old_lines, new_lines, expected_old, expected_new
):
    previous, current = _pair(tmp_path, old_lines, new_lines)
    result = build_source_diff(previous, current, DiffMode.SUMMARY)
    omitted = [row for row in result.rows if row.kind == "OMITTED"]
    assert omitted
    assert sum(row.omitted_old for row in omitted) == expected_old
    assert sum(row.omitted_new for row in omitted) == expected_new
    assert result.omitted_old == expected_old
    assert result.omitted_new == expected_new


def test_summary_boundary_is_complete_at_threshold(tmp_path):
    lines = [f"old {index}" for index in range(15)]
    previous, current = _pair(tmp_path, lines, [line.replace("old", "new") for line in lines])
    result = build_source_diff(previous, current, DiffMode.SUMMARY)
    assert len(result.rows) == 15
    assert result.omitted_total == 0


def test_summary_omits_above_threshold(tmp_path):
    lines = [f"old {index}" for index in range(16)]
    previous, current = _pair(tmp_path, lines, [line.replace("old", "new") for line in lines])
    result = build_source_diff(previous, current, DiffMode.SUMMARY)
    assert len(result.rows) == SUMMARY_CONTEXT_LINES * 2 + 1
    assert result.rows[SUMMARY_CONTEXT_LINES].kind == "OMITTED"


def test_skip_returns_no_rows(tmp_path):
    previous, current = _pair(tmp_path, ["old"], ["new"])
    result = build_source_diff(previous, current, DiffMode.SKIP)
    assert result.rows == ()
    assert result.source_available


def test_binary_source_is_explicitly_unavailable(tmp_path):
    previous, current = _pair(tmp_path, ["old"], ["new"], suffix=".usdc")
    result = build_source_diff(previous, current, DiffMode.FULL)
    assert result.rows == ()
    assert not result.source_available


def test_invalid_utf8_is_explicitly_unavailable(tmp_path):
    previous = tmp_path / "previous.usda"
    current = tmp_path / "current.usda"
    previous.write_bytes(b"\xff\xfe")
    current.write_bytes(b"\xff\xfe")
    result = build_source_diff(previous, current, DiffMode.FULL)
    assert result.rows == ()
    assert not result.source_available


def test_progress_switches_between_determinate_and_indeterminate(tmp_path):
    previous, current = _pair(tmp_path, [f"old {i}" for i in range(30)], [f"new {i}" for i in range(30)])
    updates = []
    build_source_diff(previous, current, DiffMode.FULL, progress=updates.append)
    assert any(update.phase == "align" and not update.determinate for update in updates)
    assert any(update.phase == "full_rows" and update.determinate for update in updates)
    assert updates[-1].percent == 100


def test_cancellation_token_is_deterministic():
    token = CancellationToken()
    token.raise_if_cancelled()
    token.cancel()
    assert token.cancelled
    with pytest.raises(ComparisonCancelled):
        token.raise_if_cancelled()


def test_progress_percent_is_bounded():
    assert ProgressUpdate("x", "x", 150, 100).percent == 100
    assert ProgressUpdate("x", "x", -10, 100).percent == 0
    assert ProgressUpdate("x", "x").percent is None
