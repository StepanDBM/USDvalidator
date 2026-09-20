from s_usd_core.rules.common import csv_values, property_target_results, result, target_results
from s_usd_core.validation.check_ids import (
    USD_MESH_UV_INDICES_VALID,
    USD_MESH_UV_INTERPOLATION_VALID,
    USD_MESH_UV_SET_COUNT_LIMIT,
    USD_MESH_UV_SET_REQUIRED,
)


def check_mesh_uv_set_required(context, runtime_context):
    config = runtime_context.config.uvs
    invalid = [item.mesh_path for item in context.lookdev.surfaces if config.required and config.required_set_name not in item.uv_sets]
    return result(USD_MESH_UV_SET_REQUIRED, "Mesh UV Set Required", "UVs", runtime_context, not invalid, f"Meshes missing UV set {config.required_set_name!r}: {len(invalid)}.", details={"paths": invalid, "required": config.required}, targets=target_results(context.lookdev.surfaces, lambda item: item.mesh_path, lambda item: config.required and config.required_set_name not in item.uv_sets, property_name=lambda item: f"primvars:{config.required_set_name}", observed=lambda item: tuple(item.uv_sets), expected=config.required_set_name))


def check_mesh_uv_set_count_limit(context, runtime_context):
    limit = runtime_context.config.uvs.maximum_sets_per_mesh
    invalid = {item.mesh_path: len(item.uv_sets) for item in context.lookdev.surfaces if len(item.uv_sets) > limit}
    return result(USD_MESH_UV_SET_COUNT_LIMIT, "Mesh UV Set Count Limit", "UVs", runtime_context, not invalid, f"Meshes exceeding {limit} UV sets: {len(invalid)}.", details={"meshes": invalid, "limit": limit}, targets=target_results(context.lookdev.surfaces, lambda item: item.mesh_path, lambda item: len(item.uv_sets) > limit, observed=lambda item: len(item.uv_sets), expected=lambda item: f"<= {limit}"))


def check_mesh_uv_indices_valid(context, runtime_context):
    evaluated = [(item, name, valid) for item in context.lookdev.surfaces for name, valid in item.uv_indices_valid]
    invalid = [f"{item.mesh_path}:{name}" for item, name, valid in evaluated if not valid]
    return result(USD_MESH_UV_INDICES_VALID, "Mesh UV Indices Valid", "UVs", runtime_context, not invalid, f"UV sets with invalid indices: {len(invalid)}.", details={"primvars": invalid}, targets=property_target_results(evaluated, lambda row: row[0].mesh_path, lambda row: f"primvars:{row[1]}:indices", lambda row: not row[2], observed=lambda row: row[2], expected=True))


def check_mesh_uv_interpolation_valid(context, runtime_context):
    allowed = set(csv_values(runtime_context.config.uvs.allowed_interpolations_csv))
    evaluated = [(item, name, interpolation) for item in context.lookdev.surfaces for name, interpolation in item.uv_interpolations]
    invalid = [f"{item.mesh_path}:{name}" for item, name, interpolation in evaluated if interpolation not in allowed]
    return result(USD_MESH_UV_INTERPOLATION_VALID, "Mesh UV Interpolation Valid", "UVs", runtime_context, not invalid, f"UV sets using unapproved interpolation: {len(invalid)}.", details={"primvars": invalid, "allowed": sorted(allowed)}, targets=property_target_results(evaluated, lambda row: row[0].mesh_path, lambda row: f"primvars:{row[1]}", lambda row: row[2] not in allowed, observed=lambda row: row[2], expected=lambda row: tuple(sorted(allowed))))
