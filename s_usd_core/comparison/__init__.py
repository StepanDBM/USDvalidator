# comparison/__init__.py

from .engine import SemanticComparisonEngine
from .models import (
    CameraSnapshot,
    ChangeImpact,
    ChangeKind,
    ComparisonResult,
    InstancingSnapshot,
    LayerSnapshot,
    SemanticChange,
    StageComparisonSnapshot,
    SurfaceSnapshot,
)
from .progress import CancellationToken, ComparisonCancelled, ProgressUpdate
from .snapshot import StageComparisonSnapshotBuilder
from .source_preflight import (
    DiffMode,
    DiffScale,
    SourceDiffPreflight,
    inspect_source_diff,
)
from .text_diff import DiffLine, SourceDiffResult, build_side_by_side_diff, build_source_diff


__all__ = [
    "CameraSnapshot",
    "InstancingSnapshot",
    "LayerSnapshot",
    "SurfaceSnapshot",
    "ChangeImpact",
    "ChangeKind",
    "ProgressUpdate",
    "ComparisonCancelled",
    "CancellationToken",
    "ComparisonResult",
    "DiffLine",
    "DiffMode",
    "DiffScale",
    "SemanticChange",
    "SemanticComparisonEngine",
    "StageComparisonSnapshotBuilder",
    "StageComparisonSnapshot",
    "SourceDiffResult",
    "build_source_diff",
    "SourceDiffPreflight",
    "build_side_by_side_diff",
    "inspect_source_diff",
]