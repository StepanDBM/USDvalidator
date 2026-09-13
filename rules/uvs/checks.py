from rules.common import csv_values, result
from validation.check_ids import (
    USD_MESH_UV_INDICES_VALID,
    USD_MESH_UV_INTERPOLATION_VALID,
    USD_MESH_UV_SET_COUNT_LIMIT,
    USD_MESH_UV_SET_REQUIRED,
)


def check_mesh_uv_set_required(context, runtime_context):
    config = runtime_context.config.uvs
    invalid = [item.mesh_path for item in context.lookdev.surfaces if config.required and config.required_set_name not in item.uv_sets]
    return result(USD_MESH_UV_SET_REQUIRED, "Mesh UV Set Required", "UVs", runtime_context, not invalid, f"Meshes missing UV set {config.required_set_name!r}: {len(invalid)}.", details={"paths": invalid, "required": config.required})


def check_mesh_uv_set_count_limit(context, runtime_context):
    limit = runtime_context.config.uvs.maximum_sets_per_mesh
    invalid = {item.mesh_path: len(item.uv_sets) for item in context.lookdev.surfaces if len(item.uv_sets) > limit}
    return result(USD_MESH_UV_SET_COUNT_LIMIT, "Mesh UV Set Count Limit", "UVs", runtime_context, not invalid, f"Meshes exceeding {limit} UV sets: {len(invalid)}.", details={"meshes": invalid, "limit": limit})


def check_mesh_uv_indices_valid(context, runtime_context):
    invalid = [f"{item.mesh_path}:{name}" for item in context.lookdev.surfaces for name, valid in item.uv_indices_valid if not valid]
    return result(USD_MESH_UV_INDICES_VALID, "Mesh UV Indices Valid", "UVs", runtime_context, not invalid, f"UV sets with invalid indices: {len(invalid)}.", details={"primvars": invalid})


def check_mesh_uv_interpolation_valid(context, runtime_context):
    allowed = set(csv_values(runtime_context.config.uvs.allowed_interpolations_csv))
    invalid = [f"{item.mesh_path}:{name}" for item in context.lookdev.surfaces for name, interpolation in item.uv_interpolations if interpolation not in allowed]
    return result(USD_MESH_UV_INTERPOLATION_VALID, "Mesh UV Interpolation Valid", "UVs", runtime_context, not invalid, f"UV sets using unapproved interpolation: {len(invalid)}.", details={"primvars": invalid, "allowed": sorted(allowed)})
