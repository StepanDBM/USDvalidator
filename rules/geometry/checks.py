# rules/geometry/checks.py

from validation.enums import CheckStatus
from validation.models import CheckResult


def check_mesh_has_valid_points(context, runtime_context):
    invalid_meshes = [
        mesh for mesh in context.geometry.meshes
        if not mesh.points_valid
    ]

    if not invalid_meshes:
        return [CheckResult(
            check_id="USD_MESH_HAS_VALID_POINTS",
            label="Mesh Has Valid Points",
            category="Geometry",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message="All meshes have valid point data.",
            details={
                "mesh_count": len(context.geometry.meshes),
                "invalid_mesh_count": 0,
            },
        )]

    return [CheckResult(
        check_id="USD_MESH_HAS_VALID_POINTS",
        label="Mesh Has Valid Points",
        category="Geometry",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message=(
            f"{len(invalid_meshes)} mesh(es) have invalid or missing point data."
        ),
        suggestion="Ensure every mesh has a valid points attribute.",
        details={
            "mesh_count": len(context.geometry.meshes),
            "invalid_mesh_count": len(invalid_meshes),
            "meshes": [mesh.path for mesh in invalid_meshes],
        },
    )]


def check_mesh_face_vertex_counts_valid(context, runtime_context):
    invalid_meshes = [
        mesh for mesh in context.geometry.meshes
        if not mesh.face_vertex_counts_valid
    ]

    if not invalid_meshes:
        return [CheckResult(
            check_id="USD_MESH_FACE_VERTEX_COUNTS_VALID",
            label="Mesh Face Vertex Counts Valid",
            category="Geometry",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message="All meshes have valid face vertex counts.",
            details={
                "mesh_count": len(context.geometry.meshes),
                "invalid_mesh_count": 0,
            },
        )]

    return [CheckResult(
        check_id="USD_MESH_FACE_VERTEX_COUNTS_VALID",
        label="Mesh Face Vertex Counts Valid",
        category="Geometry",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message=(
            f"{len(invalid_meshes)} mesh(es) have invalid face vertex counts."
        ),
        suggestion=(
            "Ensure faceVertexCounts contains a valid positive vertex count "
            "for every face."
        ),
        details={
            "mesh_count": len(context.geometry.meshes),
            "invalid_mesh_count": len(invalid_meshes),
            "meshes": [mesh.path for mesh in invalid_meshes],
        },
    )]


def check_mesh_has_valid_topology(context, runtime_context):
    invalid_meshes = [
        mesh for mesh in context.geometry.meshes
        if not mesh.topology_valid
    ]

    if not invalid_meshes:
        return [CheckResult(
            check_id="USD_MESH_HAS_VALID_TOPOLOGY",
            label="Mesh Has Valid Topology",
            category="Geometry",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message="All meshes have valid topology.",
            details={
                "mesh_count": len(context.geometry.meshes),
                "invalid_mesh_count": 0,
            },
        )]

    return [CheckResult(
        check_id="USD_MESH_HAS_VALID_TOPOLOGY",
        label="Mesh Has Valid Topology",
        category="Geometry",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message=(
            f"{len(invalid_meshes)} mesh(es) have invalid topology."
        ),
        suggestion=(
            "Verify that faceVertexIndices and faceVertexCounts describe "
            "a valid mesh topology."
        ),
        details={
            "mesh_count": len(context.geometry.meshes),
            "invalid_mesh_count": len(invalid_meshes),
            "meshes": [mesh.path for mesh in invalid_meshes],
        },
    )]


def check_mesh_polygon_count_limit(context, runtime_context):
    exceeding_meshes = [
        mesh for mesh in context.geometry.meshes
        if mesh.polygon_count > context.geometry.polygon_count_limit
    ]

    if not exceeding_meshes:
        return [CheckResult(
            check_id="USD_MESH_POLYGON_COUNT_LIMIT",
            label="Mesh Polygon Count Limit",
            category="Geometry",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message=(
                f"All meshes are within the polygon limit of "
                f"{context.geometry.polygon_count_limit}."
            ),
            details={
                "polygon_count_limit": context.geometry.polygon_count_limit,
                "exceeding_mesh_count": 0,
            },
        )]

    return [CheckResult(
        check_id="USD_MESH_POLYGON_COUNT_LIMIT",
        label="Mesh Polygon Count Limit",
        category="Geometry",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message=(
            f"{len(exceeding_meshes)} mesh(es) exceed the polygon limit of "
            f"{context.geometry.polygon_count_limit}."
        ),
        suggestion=(
            "Reduce mesh polygon counts or adjust the publish polygon limit "
            "for the target asset."
        ),
        details={
            "polygon_count_limit": context.geometry.polygon_count_limit,
            "exceeding_mesh_count": len(exceeding_meshes),
            "meshes": [
                {
                    "path": mesh.path,
                    "polygon_count": mesh.polygon_count,
                }
                for mesh in exceeding_meshes
            ],
        },
    )]