from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from .source_preflight import DiffMode


SUMMARY_CONTEXT_LINES = 3
SUMMARY_REGION_THRESHOLD = 15
BINARY_MESSAGE = "Binary USD source. Text diff is unavailable."


class DiffCancelled(Exception):
    pass


@dataclass(frozen=True)
class DiffLine:
    old_number: int | None
    new_number: int | None
    old_text: str
    new_text: str
    kind: str
    omitted_old: int = 0
    omitted_new: int = 0


@dataclass(frozen=True)
class SourceDiffResult:
    mode: DiffMode
    rows: tuple[DiffLine, ...]
    previous_line_count: int
    current_line_count: int
    omitted_old: int = 0
    omitted_new: int = 0

    @property
    def omitted_total(self):
        return self.omitted_old + self.omitted_new


def build_side_by_side_diff(previous_path, current_path, mode=DiffMode.FULL):
    return build_source_diff(previous_path, current_path, mode).rows


def build_source_diff(previous_path, current_path, mode=DiffMode.FULL, cancelled=None):
    old_lines = _read_lines(previous_path)
    new_lines = _read_lines(current_path)
    if mode is DiffMode.SKIP:
        return SourceDiffResult(mode, (), len(old_lines), len(new_lines))

    _check_cancelled(cancelled)
    matcher = SequenceMatcher(None, old_lines, new_lines, autojunk=True)
    rows = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        _check_cancelled(cancelled)
        builder = _summary_opcode if mode is DiffMode.SUMMARY else _full_opcode
        rows.extend(builder(tag, i1, i2, j1, j2, old_lines, new_lines))

    omitted_old = sum(row.omitted_old for row in rows)
    omitted_new = sum(row.omitted_new for row in rows)
    return SourceDiffResult(
        mode,
        tuple(rows),
        len(old_lines),
        len(new_lines),
        omitted_old,
        omitted_new,
    )


def _full_opcode(tag, i1, i2, j1, j2, old_lines, new_lines):
    return [
        _opcode_line(tag, offset, i1, i2, j1, j2, old_lines, new_lines)
        for offset in range(max(i2 - i1, j2 - j1))
    ]


def _summary_opcode(tag, i1, i2, j1, j2, old_lines, new_lines):
    count = max(i2 - i1, j2 - j1)
    if count <= SUMMARY_REGION_THRESHOLD:
        return _full_opcode(tag, i1, i2, j1, j2, old_lines, new_lines)

    context = SUMMARY_CONTEXT_LINES
    offsets = tuple(range(context)) + tuple(range(count - context, count))
    rows = [
        _opcode_line(tag, offset, i1, i2, j1, j2, old_lines, new_lines)
        for offset in offsets
    ]
    old_omitted = max(0, i2 - i1 - context * 2)
    new_omitted = max(0, j2 - j1 - context * 2)
    rows.insert(context, _omission_line(tag, old_omitted, new_omitted))
    return rows


def _opcode_line(tag, offset, i1, i2, j1, j2, old_lines, new_lines):
    old_index = i1 + offset
    new_index = j1 + offset
    old_valid = old_index < i2
    new_valid = new_index < j2
    kind = {
        "equal": "UNCHANGED",
        "delete": "REMOVED",
        "insert": "ADDED",
        "replace": "CHANGED",
    }[tag]
    return DiffLine(
        old_index + 1 if old_valid and tag != "insert" else None,
        new_index + 1 if new_valid and tag != "delete" else None,
        old_lines[old_index] if old_valid and tag != "insert" else "",
        new_lines[new_index] if new_valid and tag != "delete" else "",
        kind,
    )


def _omission_line(tag, old_count, new_count):
    if tag == "equal":
        message = f"... {old_count:,} unchanged lines omitted by Summary Diff ..."
        return DiffLine(None, None, message, message, "OMITTED", old_count, new_count)

    old_text = f"... {old_count:,} previous lines omitted by Summary Diff ..." if old_count else ""
    new_text = f"... {new_count:,} current lines omitted by Summary Diff ..." if new_count else ""
    return DiffLine(None, None, old_text, new_text, "OMITTED", old_count, new_count)


def _read_lines(path):
    path = Path(path)
    if path.suffix.lower() not in {".usda", ".usd"}:
        return [BINARY_MESSAGE]
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return [BINARY_MESSAGE]


def _check_cancelled(cancelled):
    if cancelled and cancelled():
        raise DiffCancelled("Source comparison cancelled.")
