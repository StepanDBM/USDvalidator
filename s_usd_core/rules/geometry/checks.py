# rules/geometry/checks.py

from s_usd_core.validation.check_ids import *
from s_usd_core.validation.enums import CheckStatus
from s_usd_core.validation.models import CheckResult
from s_usd_core.rules.common import target_results

def _result(check_id, label, category, runtime, passed, message, details=None, suggestion=""):
    return [CheckResult(
        check_id=check_id,
        label=label,
        category=category,
        status=CheckStatus.PASSED if passed else CheckStatus.FAILED,
        severity=runtime.default_severity,
        message=message,
        suggestion=suggestion,
        details=details or {},
    )]


def _invalid(context, predicate):
    return [mesh for mesh in context.geometry.meshes if predicate(mesh)]


def _mesh_result(check_id, label, runtime, meshes, invalid, statement, suggestion, property_name="", observed=None, expected=None):
    invalid_ids = {id(mesh) for mesh in invalid}
    targets = target_results(
        meshes, lambda mesh: mesh.path, lambda mesh: id(mesh) in invalid_ids,
        property_name=property_name, observed=observed, expected=expected,
        message=lambda mesh: statement if id(mesh) in invalid_ids else f"Passes {label.lower()}.",
    )
    result = _result(
        check_id, label, "Geometry", runtime, not invalid,
        statement if invalid else f"All meshes pass {label.lower()}.",
        {"invalid_meshes": [mesh.path for mesh in invalid]}, suggestion,
    )[0]
    result.targets = targets
    return [result]


def check_mesh_has_valid_points(context, runtime_context):
    invalid = _invalid(context, lambda mesh: not mesh.points_valid)
    return _mesh_result(USD_MESH_HAS_VALID_POINTS, "Mesh Has Valid Points", runtime_context, context.geometry.meshes, invalid, f"{len(invalid)} mesh(es) have invalid points.", "Author valid mesh points.", "points", lambda mesh: mesh.points_count, "Non-empty finite point3 values")


def check_mesh_face_vertex_counts_valid(context, runtime_context):
    invalid = _invalid(context, lambda mesh: not mesh.face_vertex_counts_valid)
    return _mesh_result(USD_MESH_FACE_VERTEX_COUNTS_VALID, "Mesh Face Vertex Counts Valid", runtime_context, context.geometry.meshes, invalid, f"{len(invalid)} mesh(es) have invalid faceVertexCounts.", "Repair face vertex counts.", "faceVertexCounts", lambda mesh: mesh.face_count, "Counts compatible with point count")


def check_mesh_has_valid_topology(context, runtime_context):
    invalid = _invalid(context, lambda mesh: not mesh.topology_valid)
    return _mesh_result(USD_MESH_HAS_VALID_TOPOLOGY, "Mesh Has Valid Topology", runtime_context, context.geometry.meshes, invalid, f"{len(invalid)} mesh(es) have invalid topology.", "Repair mesh topology.", "faceVertexIndices", lambda mesh: mesh.topology_valid, True)


def check_mesh_polygon_count_limit(context, runtime_context):
    limit = runtime_context.config.geometry.polygon_count_limit
    invalid = _invalid(context, lambda mesh: mesh.polygon_count > limit)
    return _mesh_result(USD_MESH_POLYGON_COUNT_LIMIT, "Mesh Polygon Count Limit", runtime_context, context.geometry.meshes, invalid, f"{len(invalid)} mesh(es) exceed {limit} polygons.", "Reduce mesh polygon counts or override the profile limit.", observed=lambda mesh: mesh.polygon_count, expected=lambda mesh: f"<= {limit}")


def check_mesh_point_count_limit(context, runtime_context):
    limit = runtime_context.config.geometry.point_count_limit
    invalid = _invalid(context, lambda mesh: mesh.points_count > limit)
    return _mesh_result(USD_MESH_POINT_COUNT_LIMIT, "Mesh Point Count Limit", runtime_context, context.geometry.meshes, invalid, f"{len(invalid)} mesh(es) exceed {limit} points.", "Reduce mesh point counts or override the profile limit.", "points", lambda mesh: mesh.points_count, lambda mesh: f"<= {limit}")


def check_stage_total_polygon_count_limit(context, runtime_context):
    count = context.geometry.total_polygons
    limit = runtime_context.config.geometry.total_polygon_count_limit
    return _result(USD_STAGE_TOTAL_POLYGON_COUNT_LIMIT, "Stage Total Polygon Count Limit", "Geometry", runtime_context, count <= limit, f"Stage polygon count {count}; allowed maximum {limit}.", {"total_polygons": count, "limit": limit}, "Reduce total geometry complexity.")


def check_stage_mesh_count_limit(context, runtime_context):
    count = context.geometry.mesh_count
    limit = runtime_context.config.geometry.mesh_count_limit
    return _result(USD_STAGE_MESH_COUNT_LIMIT, "Stage Mesh Count Limit", "Geometry", runtime_context, count <= limit, f"Stage mesh count {count}; allowed maximum {limit}.", {"mesh_count": count, "limit": limit}, "Consolidate or instance repeated geometry.")


def check_mesh_has_extent(context, runtime_context):
    required = runtime_context.config.geometry.require_extent
    invalid = _invalid(context, lambda mesh: required and not mesh.extent_authored)
    return _mesh_result(USD_MESH_HAS_EXTENT, "Mesh Has Extent", runtime_context, context.geometry.meshes, invalid, f"{len(invalid)} mesh(es) have no authored extent.", "Author or compute extents before publishing.", "extent", lambda mesh: mesh.extent_authored, True)


def check_mesh_subdivision_scheme_valid(context, runtime_context):
    allowed = runtime_context.config.geometry.allowed_subdivision_schemes
    invalid = _invalid(context, lambda mesh: mesh.subdivision_scheme not in allowed)
    return _mesh_result(USD_MESH_SUBDIVISION_SCHEME_VALID, "Mesh Subdivision Scheme Valid", runtime_context, context.geometry.meshes, invalid, f"{len(invalid)} mesh(es) use unsupported subdivision schemes.", f"Use one of: {', '.join(allowed)}.", "subdivisionScheme", lambda mesh: mesh.subdivision_scheme, lambda mesh: tuple(allowed))


def check_mesh_orientation_valid(context, runtime_context):
    allowed = runtime_context.config.geometry.allowed_orientations
    invalid = _invalid(context, lambda mesh: mesh.orientation not in allowed)
    return _mesh_result(USD_MESH_ORIENTATION_VALID, "Mesh Orientation Valid", runtime_context, context.geometry.meshes, invalid, f"{len(invalid)} mesh(es) use unsupported orientation.", f"Use one of: {', '.join(allowed)}.", "orientation", lambda mesh: mesh.orientation, lambda mesh: tuple(allowed))