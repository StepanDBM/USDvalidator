from rules.common import csv_values, result
from validation.check_ids import (
    USD_MESH_NORMALS_AUTHORED,
    USD_MESH_NORMALS_COUNT_VALID,
    USD_MESH_NORMALS_FINITE,
    USD_MESH_NORMALS_INTERPOLATION_VALID,
)


def check_mesh_normals_authored(context, runtime_context):
    required = runtime_context.config.normals.require_authored
    invalid = [item.mesh_path for item in context.lookdev.surfaces if required and not item.normals_authored]
    return result(USD_MESH_NORMALS_AUTHORED, "Mesh Normals Authored", "Normals", runtime_context, not invalid, f"Meshes without authored normals: {len(invalid)}.", details={"paths": invalid, "required": required})


def check_mesh_normals_finite(context, runtime_context):
    invalid = [item.mesh_path for item in context.lookdev.surfaces if not item.normals_finite]
    return result(USD_MESH_NORMALS_FINITE, "Mesh Normals Finite", "Normals", runtime_context, not invalid, f"Meshes containing non-finite normals: {len(invalid)}.", details={"paths": invalid})


def check_mesh_normals_count_valid(context, runtime_context):
    invalid = []
    for item in context.lookdev.surfaces:
        if not item.normals_authored:
            continue
        expected = {
            "constant": 1,
            "vertex": item.point_count,
            "varying": item.point_count,
            "faceVarying": item.face_vertex_count,
        }.get(item.normals_interpolation)
        if expected is not None and item.normals_count != expected:
            invalid.append(item.mesh_path)
    return result(USD_MESH_NORMALS_COUNT_VALID, "Mesh Normals Count Valid", "Normals", runtime_context, not invalid, f"Meshes with incompatible normal counts: {len(invalid)}.", details={"paths": invalid})


def check_mesh_normals_interpolation_valid(context, runtime_context):
    allowed = set(csv_values(runtime_context.config.normals.allowed_interpolations_csv))
    invalid = [item.mesh_path for item in context.lookdev.surfaces if item.normals_authored and item.normals_interpolation not in allowed]
    return result(USD_MESH_NORMALS_INTERPOLATION_VALID, "Mesh Normals Interpolation Valid", "Normals", runtime_context, not invalid, f"Meshes using unapproved normal interpolation: {len(invalid)}.", details={"paths": invalid, "allowed": sorted(allowed)})
