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
class NamingRuleConfig:
    prim_name_pattern: str = r"^[A-Za-z_][A-Za-z0-9_]*$"
    forbidden_tokens_csv: str = "temp,tmp,backup,copy"
    forbidden_names_csv: str = "pCube1,meshShape1,group1"
    case_sensitive: bool = False


@dataclass
class HierarchyRuleConfig:
    require_single_root: bool = True
    required_paths_csv: str = "/World"
    geometry_root_path: str = "/World/Geometry"
    require_meshes_under_geometry_root: bool = False


@dataclass
class TransformRuleConfig:
    require_identity_root: bool = True
    allow_negative_scale: bool = False
    allow_matrix_ops: bool = True
    maximum_xform_ops: int = 8
    zero_scale_tolerance: float = 0.000001


@dataclass
class VariantRuleConfig:
    required_sets_csv: str = ""
    require_authored_selections: bool = True
    maximum_sets_per_prim: int = 8


@dataclass
class CameraRuleConfig:
    required: bool = False
    maximum_count: int = 8
    render_camera_name: str = "RenderCamera"
    require_render_camera: bool = False
    minimum_focal_length: float = 1.0
    maximum_focal_length: float = 500.0
    minimum_near_clip: float = 0.0001
    maximum_far_clip: float = 10000000.0
    allow_animation: bool = True


@dataclass
class InstancingRuleConfig:
    maximum_instances: int = 100000
    maximum_point_instances: int = 1000000
    require_valid_prototypes: bool = False


@dataclass
class PackagingRuleConfig:
    allow_parent_directory_escape: bool = False
    allow_absolute_dependency_paths: bool = False
    allow_temporary_dependencies: bool = False
    maximum_dependency_count: int = 10000
    allowed_extensions_csv: str = ".usd,.usda,.usdc,.usdz"
    filename_pattern: str = r"^[A-Za-z0-9_.-]+$"

@dataclass
class ValidationRuleConfig:
    stage: StageRuleConfig = field(default_factory=StageRuleConfig)
    geometry: GeometryRuleConfig = field(default_factory=GeometryRuleConfig)
    metadata: MetadataRuleConfig = field(default_factory=MetadataRuleConfig)
    composition: CompositionRuleConfig = field(default_factory=CompositionRuleConfig)
    animation: AnimationRuleConfig = field(default_factory=AnimationRuleConfig)
    naming: NamingRuleConfig = field(default_factory=NamingRuleConfig)
    hierarchy: HierarchyRuleConfig = field(default_factory=HierarchyRuleConfig)
    transforms: TransformRuleConfig = field(default_factory=TransformRuleConfig)
    variants: VariantRuleConfig = field(default_factory=VariantRuleConfig)
    cameras: CameraRuleConfig = field(default_factory=CameraRuleConfig)
    instancing: InstancingRuleConfig = field(default_factory=InstancingRuleConfig)
    packaging: PackagingRuleConfig = field(default_factory=PackagingRuleConfig)
