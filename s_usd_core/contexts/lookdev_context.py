from dataclasses import dataclass, field


@dataclass(frozen=True)
class MaterialInfo:
    path: str
    surface_connected: bool
    displacement_connected: bool
    volume_connected: bool
    output_count: int


@dataclass(frozen=True)
class ShaderInfo:
    path: str
    shader_id: str
    implementation_source: str
    input_count: int
    output_count: int
    connected_input_count: int
    asset_inputs: tuple[str, ...]


@dataclass(frozen=True)
class MaterialBindingInfo:
    prim_path: str
    material_path: str
    direct: bool
    resolved: bool


@dataclass(frozen=True)
class SurfaceInfo:
    mesh_path: str
    point_count: int
    face_vertex_count: int
    normals_authored: bool
    normals_count: int
    normals_interpolation: str
    normals_finite: bool
    uv_sets: tuple[str, ...]
    uv_counts: tuple[tuple[str, int], ...]
    uv_interpolations: tuple[tuple[str, str], ...]
    uv_indices_valid: tuple[tuple[str, bool], ...]


@dataclass(frozen=True)
class LayerInfo:
    identifier: str
    anonymous: bool
    dirty: bool
    sublayer_count: int
    documentation: str
    default_prim: str


@dataclass
class LookdevStatistics:
    materials: list[MaterialInfo] = field(default_factory=list)
    shaders: list[ShaderInfo] = field(default_factory=list)
    bindings: list[MaterialBindingInfo] = field(default_factory=list)
    surfaces: list[SurfaceInfo] = field(default_factory=list)
    layers: list[LayerInfo] = field(default_factory=list)
