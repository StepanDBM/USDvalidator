from dataclasses import dataclass
from enum import Enum
from pathlib import Path


NORMAL_LINE_LIMIT = 100000
EXTREME_LINE_LIMIT = 1000000
NORMAL_BYTE_LIMIT = 50 * 1024 * 1024
EXTREME_BYTE_LIMIT = 250 * 1024 * 1024


class DiffMode(str, Enum):
    FULL = "FULL"
    SUMMARY = "SUMMARY"
    SKIP = "SKIP"


class DiffScale(str, Enum):
    NORMAL = "NORMAL"
    LARGE = "LARGE"
    EXTREME = "EXTREME"


@dataclass(frozen=True)
class SourceDiffPreflight:
    previous_bytes: int
    current_bytes: int
    previous_lines: int | None
    current_lines: int | None
    textual: bool
    scale: DiffScale

    @property
    def total_bytes(self):
        return self.previous_bytes + self.current_bytes

    @property
    def total_lines(self):
        if self.previous_lines is None or self.current_lines is None:
            return None
        return self.previous_lines + self.current_lines


def inspect_source_diff(previous_path, current_path):
    previous = Path(previous_path)
    current = Path(current_path)
    textual = all(path.suffix.lower() in {".usd", ".usda"} for path in (previous, current))
    previous_bytes = previous.stat().st_size
    current_bytes = current.stat().st_size

    if not textual:
        return SourceDiffPreflight(
            previous_bytes,
            current_bytes,
            None,
            None,
            False,
            DiffScale.NORMAL,
        )

    previous_lines = _count_lines(previous)
    current_lines = _count_lines(current)
    total_lines = previous_lines + current_lines
    total_bytes = previous_bytes + current_bytes

    if total_lines > EXTREME_LINE_LIMIT or total_bytes > EXTREME_BYTE_LIMIT:
        scale = DiffScale.EXTREME
    elif total_lines > NORMAL_LINE_LIMIT or total_bytes > NORMAL_BYTE_LIMIT:
        scale = DiffScale.LARGE
    else:
        scale = DiffScale.NORMAL

    return SourceDiffPreflight(
        previous_bytes,
        current_bytes,
        previous_lines,
        current_lines,
        True,
        scale,
    )


def _count_lines(path):
    count = 0
    last = b""
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            count += chunk.count(b"\n")
            last = chunk[-1:]
    return count + int(path.stat().st_size > 0 and last != b"\n")
