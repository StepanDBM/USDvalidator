from dataclasses import dataclass, field


@dataclass
class MeshGeometry:
    path: str = ""
    points_count: int = 0
    face_count: int = 0
    polygon_count: int = 0

    points_valid: bool = False
    face_vertex_counts_valid: bool = False
    topology_valid: bool = False


@dataclass
class GeometryStatistics:
    mesh_count: int = 0
    total_points: int = 0
    total_faces: int = 0
    total_polygons: int = 0

    meshes: list[MeshGeometry] = field(default_factory=list)

    polygon_count_limit: int = 100000