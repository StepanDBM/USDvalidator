# contexts/stage_health_context.py

from dataclasses import dataclass, field
from .geometry_context import GeometryStatistics


@dataclass
class FileHealth:
    filename: str = ""
    extension: str = ""
    size_bytes: int = 0
    modification_time: float | None = None


@dataclass
class StageMetadata:
    open_duration_seconds: float = 0.0
    root_layer: str = ""
    default_prim: str = ""
    default_prim_valid: bool | None = None
    up_axis: str = ""
    meters_per_unit: float | None = None
    frames_per_second: float | None = None
    time_codes_per_second: float | None = None
    start_time_code: float | None = None
    end_time_code: float | None = None


@dataclass
class SceneStatistics:
    total_prims: int = 0
    root_prims: int = 0
    active_prims: int = 0
    inactive_prims: int = 0
    defined_prims: int = 0
    abstract_prims: int = 0
    instance_prims: int = 0


@dataclass
class TypeCounts:
    meshes: int = 0
    xforms: int = 0
    cameras: int = 0
    lights: int = 0
    materials: int = 0
    curves: int = 0
    point_instancers: int = 0


@dataclass
class CompositionStatistics:
    used_layers: int = 0
    sublayers: int = 0
    references: int = 0
    payloads: int = 0
    variant_sets: int = 0
    unresolved_references: int = 0
    unresolved_payloads: int = 0
    invalid_layers: int = 0
    unexpected_arcs: int = 0

@dataclass
class StageHealthContext:
    file: FileHealth = field(default_factory=FileHealth)
    stage: StageMetadata = field(default_factory=StageMetadata)
    scene: SceneStatistics = field(default_factory=SceneStatistics)
    types: TypeCounts = field(default_factory=TypeCounts)
    composition: CompositionStatistics = field(default_factory=CompositionStatistics)
    geometry: GeometryStatistics = field(default_factory=GeometryStatistics)