from dataclasses import dataclass, field


@dataclass(frozen=True)
class PrimInfo:
    path: str
    name: str
    parent_path: str
    type_name: str
    depth: int


@dataclass(frozen=True)
class TransformInfo:
    path: str
    op_names: tuple[str, ...]
    resets_stack: bool
    time_varying: bool
    matrix_op_count: int
    scale_values: tuple[tuple[float, float, float], ...]
    values_finite: bool
    local_transform_identity: bool


@dataclass(frozen=True)
class VariantSetInfo:
    prim_path: str
    name: str
    variants: tuple[str, ...]
    selection: str


@dataclass(frozen=True)
class CameraInfo:
    path: str
    projection: str
    focal_length: float
    clipping_range: tuple[float, float]
    time_varying: bool


@dataclass(frozen=True)
class InstancingInfo:
    path: str
    instance: bool
    instanceable: bool
    prototype_path: str
    point_instancer: bool
    prototype_count: int
    point_instance_count: int
    invalid_proto_indices: int


@dataclass(frozen=True)
class DependencyInfo:
    prim_path: str
    arc_type: str
    asset_path: str
    absolute: bool
    parent_escape: bool
    temporary: bool


@dataclass
class PipelineStatistics:
    prims: list[PrimInfo] = field(default_factory=list)
    transforms: list[TransformInfo] = field(default_factory=list)
    variants: list[VariantSetInfo] = field(default_factory=list)
    cameras: list[CameraInfo] = field(default_factory=list)
    instances: list[InstancingInfo] = field(default_factory=list)
    dependencies: list[DependencyInfo] = field(default_factory=list)
