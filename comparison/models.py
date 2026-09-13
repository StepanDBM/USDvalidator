from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import json
from pathlib import Path


class ChangeImpact(str, Enum):
    INFORMATIONAL = "INFORMATIONAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


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
    domain: str = ""
    property_path: str = ""
    impact: ChangeImpact = ChangeImpact.LOW
    why_it_matters: str = ""
    related_check_ids: tuple[str, ...] = ()
    source_hint: str = ""
    validation_consequence: str = ""

    @property
    def subject_path(self):
        return self.path


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
class TransformSnapshot:
    path: str
    op_names: tuple[str, ...]
    resets_stack: bool
    time_varying: bool
    matrix_op_count: int
    scale_values: tuple[tuple[float, float, float], ...]
    values_finite: bool
    local_transform_identity: bool


@dataclass(frozen=True)
class VariantSnapshot:
    prim_path: str
    name: str
    variants: tuple[str, ...]
    selection: str


@dataclass(frozen=True)
class MaterialSnapshot:
    path: str
    surface_connected: bool
    displacement_connected: bool
    volume_connected: bool
    output_count: int


@dataclass(frozen=True)
class ShaderSnapshot:
    path: str
    shader_id: str
    implementation_source: str
    input_count: int
    output_count: int
    connected_input_count: int
    asset_inputs: tuple[str, ...]
    input_values: tuple[tuple[str, str], ...] = ()
    connections: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class MaterialBindingSnapshot:
    prim_path: str
    material_path: str
    direct: bool
    resolved: bool


@dataclass(frozen=True)
class SurfaceSnapshot:
    path: str
    normals_authored: bool
    normals_count: int
    normals_interpolation: str
    normals_finite: bool
    uv_sets: tuple[str, ...]
    uv_counts: tuple[tuple[str, int], ...]
    uv_interpolations: tuple[tuple[str, str], ...]
    uv_indices_valid: tuple[tuple[str, bool], ...]


@dataclass(frozen=True)
class LayerSnapshot:
    identifier: str
    anonymous: bool
    dirty: bool
    sublayer_count: int
    documentation: str
    default_prim: str


@dataclass(frozen=True)
class CameraSnapshot:
    path: str
    projection: str
    focal_length: float
    clipping_range: tuple[float, float]
    time_varying: bool


@dataclass(frozen=True)
class InstancingSnapshot:
    path: str
    instance: bool
    instanceable: bool
    prototype_path: str
    point_instancer: bool
    prototype_count: int
    point_instance_count: int
    invalid_proto_indices: int


@dataclass(frozen=True)
class StageComparisonSnapshot:
    source_path: str
    metadata: dict
    prims: dict[str, PrimSnapshot]
    meshes: dict[str, MeshSnapshot]
    dependencies: tuple[DependencySnapshot, ...]
    animation: dict[str, AnimationSnapshot]
    transforms: dict[str, TransformSnapshot] = field(default_factory=dict)
    variants: dict[tuple[str, str], VariantSnapshot] = field(default_factory=dict)
    materials: dict[str, MaterialSnapshot] = field(default_factory=dict)
    shaders: dict[str, ShaderSnapshot] = field(default_factory=dict)
    material_bindings: dict[str, MaterialBindingSnapshot] = field(default_factory=dict)
    surfaces: dict[str, SurfaceSnapshot] = field(default_factory=dict)
    layers: dict[str, LayerSnapshot] = field(default_factory=dict)
    cameras: dict[str, CameraSnapshot] = field(default_factory=dict)
    instancing: dict[str, InstancingSnapshot] = field(default_factory=dict)
    dependency_map: dict[tuple[str, str, str, str], DependencySnapshot] = field(default_factory=dict)
    sublayers: tuple[SublayerSnapshot, ...] = ()
    composition_arcs: dict[tuple[str, str, str], CompositionArcSnapshot] = field(default_factory=dict)
    path_arcs: dict[tuple[str, str, str], PathArcSnapshot] = field(default_factory=dict)
    relationships: dict[str, RelationshipSnapshot] = field(default_factory=dict)
    collections: dict[tuple[str, str], CollectionSnapshot] = field(default_factory=dict)
    geom_subsets: dict[str, GeomSubsetSnapshot] = field(default_factory=dict)
    primvars: dict[str, PrimvarSnapshot] = field(default_factory=dict)
    lights: dict[str, LightSnapshot] = field(default_factory=dict)
    render_settings: dict[str, RenderSettingsSnapshot] = field(default_factory=dict)
    render_products: dict[str, RenderProductSnapshot] = field(default_factory=dict)
    render_vars: dict[str, RenderVarSnapshot] = field(default_factory=dict)
    skeletons: dict[str, SkeletonSnapshot] = field(default_factory=dict)
    skinning: dict[str, SkinningSnapshot] = field(default_factory=dict)
    blend_shapes: dict[str, BlendShapeSnapshot] = field(default_factory=dict)
    value_clips: dict[tuple[str, str], ValueClipSnapshot] = field(default_factory=dict)
    time_configuration: TimeConfigurationSnapshot | None = None


StageSnapshot = StageComparisonSnapshot


@dataclass
class ComparisonResult:
    previous_source: str
    current_source: str
    changes: list[SemanticChange] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    validation_summary_by_domain: dict[str, dict[str, int]] = field(default_factory=dict)

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
            "validation_summary_by_domain": self.validation_summary_by_domain,
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


@dataclass(frozen=True)
class SublayerSnapshot:
    layer_identifier: str
    index: int
    asset_path: str
    offset: float
    scale: float


@dataclass(frozen=True)
class CompositionArcSnapshot:
    prim_path: str
    arc_type: str
    asset_path: str
    target_prim_path: str
    list_position: str
    absolute: bool
    resolved: bool


@dataclass(frozen=True)
class PathArcSnapshot:
    prim_path: str
    arc_type: str
    target_path: str


@dataclass(frozen=True)
class RelationshipSnapshot:
    property_path: str
    targets: tuple[str, ...]
    forwarded_targets: tuple[str, ...]


@dataclass(frozen=True)
class CollectionSnapshot:
    prim_path: str
    name: str
    includes: tuple[str, ...]
    excludes: tuple[str, ...]
    expansion_rule: str
    include_root: bool


@dataclass(frozen=True)
class GeomSubsetSnapshot:
    path: str
    family_name: str
    family_type: str
    element_type: str
    element_count: int
    indices_hash: str
    material_path: str


@dataclass(frozen=True)
class PrimvarSnapshot:
    property_path: str
    type_name: str
    role: str
    interpolation: str
    element_size: int
    indexed: bool
    value_count: int
    index_count: int
    values_hash: str
    indices_hash: str
    uv_like: bool


class CorrelationConfidence(str, Enum):
    NONE = "NONE"
    CHECK_ONLY = "CHECK_ONLY"
    RELATED_PATH = "RELATED_PATH"
    EXACT = "EXACT"


@dataclass(frozen=True)
class LightSnapshot:
    path: str
    type_name: str
    intensity: str
    exposure: str
    color: str
    temperature: str
    enable_color_temperature: str
    normalize: str
    shaping: tuple[tuple[str, str], ...]
    texture_assets: tuple[str, ...]
    time_varying: bool
    linked_paths: tuple[str, ...]
    shadow_linked_paths: tuple[str, ...]


@dataclass(frozen=True)
class RenderSettingsSnapshot:
    path: str
    active: bool
    camera_path: str
    products: tuple[str, ...]
    included_purposes: tuple[str, ...]
    material_binding_purposes: tuple[str, ...]
    renderer_settings: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class RenderProductSnapshot:
    path: str
    product_type: str
    product_name: str
    camera_path: str
    ordered_vars: tuple[str, ...]
    resolution: str
    pixel_aspect_ratio: str
    data_window_ndc: str
    renderer_settings: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class RenderVarSnapshot:
    path: str
    source_name: str
    source_type: str
    data_type: str
    namespaced_settings: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class SkeletonSnapshot:
    path: str
    joints: tuple[str, ...]
    parent_indices: tuple[int, ...]
    bind_transforms_hash: str
    rest_transforms_hash: str
    animation_source: str


@dataclass(frozen=True)
class SkinningSnapshot:
    prim_path: str
    skeleton_path: str
    geom_bind_transform_hash: str
    joint_indices_hash: str
    joint_weights_hash: str
    joint_count: int
    influences_per_point: int


@dataclass(frozen=True)
class BlendShapeSnapshot:
    path: str
    offsets_hash: str
    normal_offsets_hash: str
    point_indices_hash: str
    inbetween_names: tuple[str, ...]
    bound_prims: tuple[str, ...]


@dataclass(frozen=True)
class ValueClipSnapshot:
    prim_path: str
    clip_set: str
    asset_paths: tuple[str, ...]
    clip_prim_path: str
    manifest_asset_path: str
    active_hash: str
    times_hash: str
    template_asset_path: str
    template_start_time: str
    template_end_time: str
    template_stride: str


@dataclass(frozen=True)
class TimeConfigurationSnapshot:
    start_time_code: float
    end_time_code: float
    frames_per_second: float
    time_codes_per_second: float


@dataclass(frozen=True)
class ValidationCorrelation:
    check_id: str
    previous_status: str
    current_status: str
    previous_location: str
    current_location: str
    confidence: CorrelationConfidence
    consequence: str
