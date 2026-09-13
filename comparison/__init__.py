# comparison/__init__.py

from .engine import SemanticComparisonEngine
from .models import ChangeKind, ComparisonResult, SemanticChange
from .source_preflight import (
    DiffMode,
    DiffScale,
    SourceDiffPreflight,
    inspect_source_diff,
)
from .text_diff import DiffLine, SourceDiffResult, build_side_by_side_diff, build_source_diff


__all__ = [
    "ChangeKind",
    "ComparisonResult",
    "DiffLine",
    "DiffMode",
    "DiffScale",
    "SemanticChange",
    "SemanticComparisonEngine",
    "SourceDiffResult",
    "build_source_diff",
    "SourceDiffPreflight",
    "build_side_by_side_diff",
    "inspect_source_diff",
]