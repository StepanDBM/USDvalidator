from dataclasses import asdict, dataclass, field
from enum import Enum
import json
from pathlib import Path


class ChangeKind(str, Enum):
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    CHANGED = "CHANGED"
    INCREASED = "INCREASED"
    DECREASED = "DECREASED"
    REGRESSION = "REGRESSION"
    RESOLVED = "RESOLVED"
    UNCHANGED = "UNCHANGED"


@dataclass(frozen=True)
class SemanticChange:
    category: str
    path: str
    label: str
    kind: ChangeKind
    previous: object = None
    current: object = None
    details: dict = field(default_factory=dict)


@dataclass(frozen=True)
class PrimSnapshot:
    path: str
    type_name: str
    active: bool
    defined: bool
    abstract: bool
    instance: bool
    properties: tuple[str, ...]


@dataclass(frozen=True)
class MeshSnapshot:
    path: str
    points_count: int
    face_count: int
    topology_hash: str
    points_hash: str
    extent: tuple
    subdivision_scheme: str
    orientation: str


@dataclass(frozen=True)
class DependencySnapshot:
    prim_path: str
    arc_type: str
    asset_path: str
    prim_path_in_asset: str
    resolved: bool


@dataclass(frozen=True)
class AnimationSnapshot:
    attribute_path: str
    sample_count: int
    first_sample: float | None
    last_sample: float | None
    sample_times_hash: str
    values_hash: str


@dataclass(frozen=True)
class StageSnapshot:
    source_path: str
    metadata: dict
    prims: dict[str, PrimSnapshot]
    meshes: dict[str, MeshSnapshot]
    dependencies: tuple[DependencySnapshot, ...]
    animation: dict[str, AnimationSnapshot]


@dataclass
class ComparisonResult:
    previous_source: str
    current_source: str
    changes: list[SemanticChange] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def changed(self):
        return [change for change in self.changes if change.kind is not ChangeKind.UNCHANGED]

    def count(self, kind):
        return sum(change.kind is kind for change in self.changes)

    def to_dict(self):
        return {
            "schema": {"name": "usdvalidator.semantic_comparison", "version": "1.0.0"},
            "previous_source": self.previous_source,
            "current_source": self.current_source,
            "warnings": self.warnings,
            "changes": [
                {
                    **asdict(change),
                    "kind": change.kind.value,
                }
                for change in self.changes
            ],
        }

    def write_json(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
