# rules/geometry/register.py

from contexts import StageHealthContext
from validation.enums import Severity
from validation.models import CheckDefinition

from .checks import (
    check_mesh_has_valid_points,
    check_mesh_face_vertex_counts_valid,
    check_mesh_has_valid_topology,
    check_mesh_polygon_count_limit,
)


def register_geometry_checks(registry):
    registry.register(CheckDefinition(
        check_id="USD_MESH_HAS_VALID_POINTS",
        label="Mesh Has Valid Points",
        description="Checks whether USD meshes contain valid point data.",
        func=check_mesh_has_valid_points,
        target_type=StageHealthContext,
        category="Geometry",
        phase="geometry",
        default_severity=Severity.ERROR,
        tags=("geometry", "mesh", "publish", "required"),
    ))
    registry.register(CheckDefinition(
        check_id="USD_MESH_FACE_VERTEX_COUNTS_VALID",
        label="Mesh Face Vertex Counts Valid",
        description="Checks whether mesh faceVertexCounts data is valid.",
        func=check_mesh_face_vertex_counts_valid,
        target_type=StageHealthContext,
        category="Geometry",
        phase="geometry",
        default_severity=Severity.ERROR,
        tags=("geometry", "mesh", "topology", "publish", "required"),
    ))
    registry.register(CheckDefinition(
        check_id="USD_MESH_HAS_VALID_TOPOLOGY",
        label="Mesh Has Valid Topology",
        description="Checks whether USD meshes have valid topology.",
        func=check_mesh_has_valid_topology,
        target_type=StageHealthContext,
        category="Geometry",
        phase="geometry",
        default_severity=Severity.ERROR,
        tags=("geometry", "mesh", "topology", "publish", "required"),
    ))

    registry.register(CheckDefinition(
        check_id="USD_MESH_POLYGON_COUNT_LIMIT",
        label="Mesh Polygon Count Limit",
        description="Checks whether mesh polygon counts remain within the configured limit.",
        func=check_mesh_polygon_count_limit,
        target_type=StageHealthContext,
        category="Geometry",
        phase="geometry",
        default_severity=Severity.ERROR,
        tags=("geometry", "mesh", "performance", "publish", "required"),
    ))