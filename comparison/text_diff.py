from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from .source_preflight import DiffMode


SUMMARY_CONTEXT_LINES = 3
SUMMARY_REGION_THRESHOLD = 15
BINARY_MESSAGE = "Binary USD source. Text diff is unavailable."


@dataclass(frozen=True)
class DiffLine:
    old_number: int | None
    new_number: int | None
    old_text: str
    new_text: str
    kind: str


def build_side_by_side_diff(previous_path, current_path, mode=DiffMode.FULL):
    if mode is DiffMode.SKIP:
        return ()

    old_lines = _read_lines(previous_path)
    new_lines = _read_lines(current_path)
    matcher = SequenceMatcher(None, old_lines, new_lines, autojunk=True)
    rows = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if mode is DiffMode.SUMMARY:
            rows.extend(_summary_opcode(tag, i1, i2, j1, j2, old_lines, new_lines))
        else:
            rows.extend(_full_opcode(tag, i1, i2, j1, j2, old_lines, new_lines))

    return tuple(rows)


def _full_opcode(tag, i1, i2, j1, j2, old_lines, new_lines):
    if tag == "equal":
        return [
            DiffLine(i + 1, j + 1, old_lines[i], new_lines[j], "UNCHANGED")
            for i, j in zip(range(i1, i2), range(j1, j2))
        ]

    if tag == "delete":
        return [
            DiffLine(i + 1, None, old_lines[i], "", "REMOVED")
            for i in range(i1, i2)
        ]

    if tag == "insert":
        return [
            DiffLine(None, j + 1, "", new_lines[j], "ADDED")
            for j in range(j1, j2)
        ]

    return [
        _replacement_line(offset, i1, i2, j1, j2, old_lines, new_lines)
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
    rows.insert(context, _omission_line(tag, count - context * 2, i1, i2, j1, j2))
    return rows


def _opcode_line(tag, offset, i1, i2, j1, j2, old_lines, new_lines):
    if tag == "equal":
        return DiffLine(
            i1 + offset + 1,
            j1 + offset + 1,
            old_lines[i1 + offset],
            new_lines[j1 + offset],
            "UNCHANGED",
        )

    if tag == "delete":
        old_index = i1 + offset
        return DiffLine(old_index + 1, None, old_lines[old_index], "", "REMOVED")

    if tag == "insert":
        new_index = j1 + offset
        return DiffLine(None, new_index + 1, "", new_lines[new_index], "ADDED")

    return _replacement_line(offset, i1, i2, j1, j2, old_lines, new_lines)


def _replacement_line(offset, i1, i2, j1, j2, old_lines, new_lines):
    old_index = i1 + offset
    new_index = j1 + offset
    return DiffLine(
        old_index + 1 if old_index < i2 else None,
        new_index + 1 if new_index < j2 else None,
        old_lines[old_index] if old_index < i2 else "",
        new_lines[new_index] if new_index < j2 else "",
        "CHANGED",
    )


def _omission_line(tag, omitted_count, i1, i2, j1, j2):
    old_count = max(0, i2 - i1 - SUMMARY_CONTEXT_LINES * 2)
    new_count = max(0, j2 - j1 - SUMMARY_CONTEXT_LINES * 2)

    if tag == "equal":
        message = f"... {omitted_count:,} unchanged lines omitted by Summary Diff ..."
        return DiffLine(None, None, message, message, "UNCHANGED")

    old_text = (
        f"... {old_count:,} previous lines omitted by Summary Diff ..."
        if old_count else ""
    )
    new_text = (
        f"... {new_count:,} current lines omitted by Summary Diff ..."
        if new_count else ""
    )
    return DiffLine(None, None, old_text, new_text, "CHANGED")


def _read_lines(path):
    path = Path(path)
    if path.suffix.lower() not in {".usda", ".usd"}:
        return [BINARY_MESSAGE]

    try:
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return [BINARY_MESSAGE]
