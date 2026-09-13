from dataclasses import dataclass, field


@dataclass
class StageRuleConfig:
    prim_count_limit: int = 100000
    prim_depth_limit: int = 64


@dataclass
class GeometryRuleConfig:
    polygon_count_limit: int = 100000
    point_count_limit: int = 250000
    total_polygon_count_limit: int = 1000000
    mesh_count_limit: int = 10000
    require_extent: bool = False
    allowed_subdivision_schemes: tuple[str, ...] = ("none", "catmullClark")
    allowed_orientations: tuple[str, ...] = ("rightHanded",)


@dataclass
class MetadataRuleConfig:
    allowed_up_axes: tuple[str, ...] = ("Y", "Z")
    minimum_meters_per_unit: float = 0.000001
    maximum_meters_per_unit: float = 1000.0
    required_root_prim_name: str = "World"
    allowed_root_prim_types: tuple[str, ...] = ("Xform", "Scope")


@dataclass
class CompositionRuleConfig:
    reference_count_limit: int = 1000
    payload_count_limit: int = 1000
    allow_payloads: bool = True
    require_relative_asset_paths: bool = True


@dataclass
class AnimationRuleConfig:
    allowed_frame_rates: tuple[float, ...] = (
        23.976, 24.0, 25.0, 29.97, 30.0, 48.0, 50.0, 59.94, 60.0,
    )
    maximum_frame_range: int = 10000
    maximum_time_samples: int = 1000000


@dataclass
class ValidationRuleConfig:
    stage: StageRuleConfig = field(default_factory=StageRuleConfig)
    geometry: GeometryRuleConfig = field(default_factory=GeometryRuleConfig)
    metadata: MetadataRuleConfig = field(default_factory=MetadataRuleConfig)
    composition: CompositionRuleConfig = field(default_factory=CompositionRuleConfig)
    animation: AnimationRuleConfig = field(default_factory=AnimationRuleConfig)
