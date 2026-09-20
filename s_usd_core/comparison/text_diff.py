from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from .progress import CancellationToken, ProgressUpdate
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
    source_available: bool = True

    @property
    def omitted_total(self):
        return self.omitted_old + self.omitted_new


def build_side_by_side_diff(previous_path, current_path, mode=DiffMode.FULL):
    return build_source_diff(previous_path, current_path, mode).rows


def build_source_diff(previous_path, current_path, mode=DiffMode.FULL, token=None, progress=None):
    token = token or CancellationToken()
    token.raise_if_cancelled()
    _emit(progress, "read_previous", "Reading previous source...", 0, 2)
    old_lines, old_available = _read_lines(previous_path, token)
    _emit(progress, "read_previous", "Previous source read.", 1, 2)
    token.raise_if_cancelled()
    _emit(progress, "read_current", "Reading current source...", 1, 2)
    new_lines, new_available = _read_lines(current_path, token)
    _emit(progress, "read_current", "Current source read.", 2, 2)

    source_available = old_available and new_available
    if mode is DiffMode.SKIP or not source_available:
        return SourceDiffResult(
            mode,
            (),
            len(old_lines),
            len(new_lines),
            source_available=source_available,
        )

    token.raise_if_cancelled()
    _emit(progress, "align", "Aligning source lines...")
    opcodes = SequenceMatcher(None, old_lines, new_lines, autojunk=True).get_opcodes()
    token.raise_if_cancelled()

    total = sum(max(i2 - i1, j2 - j1) for _, i1, i2, j1, j2 in opcodes)
    processed = 0
    rows = []
    phase = "summary_rows" if mode is DiffMode.SUMMARY else "full_rows"
    label = "Summary" if mode is DiffMode.SUMMARY else "Full"
    _emit(progress, phase, f"Building {label} Diff rows...", 0, max(total, 1))

    for tag, i1, i2, j1, j2 in opcodes:
        token.raise_if_cancelled()
        builder = _summary_opcode if mode is DiffMode.SUMMARY else _full_opcode
        rows.extend(builder(tag, i1, i2, j1, j2, old_lines, new_lines))
        processed += max(i2 - i1, j2 - j1)
        _emit(
            progress,
            phase,
            f"Building {label} Diff rows: {processed:,} / {total:,}",
            processed,
            max(total, 1),
        )

    token.raise_if_cancelled()
    omitted_old = sum(row.omitted_old for row in rows)
    omitted_new = sum(row.omitted_new for row in rows)
    return SourceDiffResult(
        mode,
        tuple(rows),
        len(old_lines),
        len(new_lines),
        omitted_old,
        omitted_new,
        source_available,
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


def _read_lines(path, token):
    path = Path(path)
    if path.suffix.lower() not in {".usda", ".usd"}:
        return (), False

    try:
        lines = []
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream):
                if line_number % 4096 == 0:
                    token.raise_if_cancelled()
                lines.append(line.rstrip("\r\n"))
        return lines, True
    except UnicodeDecodeError:
        return (), False


def _emit(callback, phase, message, current=None, total=None):
    if callback:
        callback(ProgressUpdate(phase, message, current, total))
