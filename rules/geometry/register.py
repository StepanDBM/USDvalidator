# rules/geometry/register.py

from contexts import StageHealthContext
from validation.check_ids import *
from validation.enums import Severity
from validation.models import CheckDefinition
from .checks import *


def register_geometry_checks(registry):
    entries = (
        (USD_MESH_HAS_VALID_POINTS, "Mesh Has Valid Points", check_mesh_has_valid_points, Severity.ERROR, ("geometry", "mesh", "required")),
        (USD_MESH_FACE_VERTEX_COUNTS_VALID, "Mesh Face Vertex Counts Valid", check_mesh_face_vertex_counts_valid, Severity.ERROR, ("geometry", "mesh", "topology")),
        (USD_MESH_HAS_VALID_TOPOLOGY, "Mesh Has Valid Topology", check_mesh_has_valid_topology, Severity.ERROR, ("geometry", "mesh", "topology")),
        (USD_MESH_POLYGON_COUNT_LIMIT, "Mesh Polygon Count Limit", check_mesh_polygon_count_limit, Severity.WARNING, ("geometry", "mesh", "budget")),
        (USD_MESH_POINT_COUNT_LIMIT, "Mesh Point Count Limit", check_mesh_point_count_limit, Severity.WARNING, ("geometry", "mesh", "budget")),
        (USD_STAGE_TOTAL_POLYGON_COUNT_LIMIT, "Stage Total Polygon Count Limit", check_stage_total_polygon_count_limit, Severity.WARNING, ("geometry", "stage", "budget")),
        (USD_STAGE_MESH_COUNT_LIMIT, "Stage Mesh Count Limit", check_stage_mesh_count_limit, Severity.WARNING, ("geometry", "stage", "budget")),
        (USD_MESH_HAS_EXTENT, "Mesh Has Extent", check_mesh_has_extent, Severity.WARNING, ("geometry", "mesh", "bounds")),
        (USD_MESH_SUBDIVISION_SCHEME_VALID, "Mesh Subdivision Scheme Valid", check_mesh_subdivision_scheme_valid, Severity.WARNING, ("geometry", "mesh", "subdivision")),
        (USD_MESH_ORIENTATION_VALID, "Mesh Orientation Valid", check_mesh_orientation_valid, Severity.ERROR, ("geometry", "mesh", "orientation")),
    )

    for check_id, label, func, severity, tags in entries:
        registry.register(CheckDefinition(
            check_id=check_id, label=label, description=label,
            func=func, target_type=StageHealthContext, category="Geometry",
            phase="geometry", default_severity=severity, tags=tags,
        ))