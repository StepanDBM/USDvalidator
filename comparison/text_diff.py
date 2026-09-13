from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path


@dataclass(frozen=True)
class DiffLine:
    old_number: int | None
    new_number: int | None
    old_text: str
    new_text: str
    kind: str


def build_side_by_side_diff(previous_path, current_path):
    old_lines = _read_lines(previous_path)
    new_lines = _read_lines(current_path)
    matcher = SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    rows = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            rows.extend(
                DiffLine(i + 1, j + 1, old_lines[i], new_lines[j], "UNCHANGED")
                for i, j in zip(range(i1, i2), range(j1, j2))
            )
        elif tag == "delete":
            rows.extend(
                DiffLine(i + 1, None, old_lines[i], "", "REMOVED")
                for i in range(i1, i2)
            )
        elif tag == "insert":
            rows.extend(
                DiffLine(None, j + 1, "", new_lines[j], "ADDED")
                for j in range(j1, j2)
            )
        else:
            count = max(i2 - i1, j2 - j1)
            for offset in range(count):
                old_index = i1 + offset
                new_index = j1 + offset
                rows.append(DiffLine(
                    old_index + 1 if old_index < i2 else None,
                    new_index + 1 if new_index < j2 else None,
                    old_lines[old_index] if old_index < i2 else "",
                    new_lines[new_index] if new_index < j2 else "",
                    "CHANGED",
                ))

    return tuple(rows)


def _read_lines(path):
    path = Path(path)

    if path.suffix.lower() not in {".usda", ".usd"}:
        return ["Binary USD source. Text diff is unavailable."]

    try:
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return ["Binary USD source. Text diff is unavailable."]
