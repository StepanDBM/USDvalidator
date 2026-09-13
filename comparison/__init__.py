# comparison/__init__.py

from .engine import SemanticComparisonEngine
from .models import ChangeKind, ComparisonResult, SemanticChange
from .source_preflight import (
    DiffMode,
    DiffScale,
    SourceDiffPreflight,
    inspect_source_diff,
)
from .text_diff import DiffLine, build_side_by_side_diff


__all__ = [
    "ChangeKind",
    "ComparisonResult",
    "DiffLine",
    "DiffMode",
    "DiffScale",
    "SemanticChange",
    "SemanticComparisonEngine",
    "SourceDiffPreflight",
    "build_side_by_side_diff",
    "inspect_source_diff",
]