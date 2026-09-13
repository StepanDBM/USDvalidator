import os

from rules.common import csv_values, result
from validation.check_ids import (
    USD_SHADER_ASSET_PATHS_RELATIVE,
    USD_SHADER_COUNT_LIMIT,
    USD_SHADER_ID_AUTHORED,
    USD_SHADER_IDS_ALLOWED,
    USD_SHADER_OUTPUTS_AUTHORED,
)


def check_shader_count_limit(context, runtime_context):
    count = len(context.lookdev.shaders)
    limit = runtime_context.config.shaders.maximum_count
    return result(USD_SHADER_COUNT_LIMIT, "Shader Count Limit", "Shaders", runtime_context, count <= limit, f"Shader count {count}; allowed maximum {limit}.", details={"count": count, "limit": limit})


def check_shader_id_authored(context, runtime_context):
    required = runtime_context.config.shaders.require_id
    invalid = [item.path for item in context.lookdev.shaders if required and not item.shader_id]
    return result(USD_SHADER_ID_AUTHORED, "Shader ID Authored", "Shaders", runtime_context, not invalid, f"Shaders without authored IDs: {len(invalid)}.", details={"paths": invalid, "required": required}, suggestion="Author an implementation ID for each shader.")


def check_shader_ids_allowed(context, runtime_context):
    allowed = set(csv_values(runtime_context.config.shaders.allowed_ids_csv))
    invalid = {item.path: item.shader_id for item in context.lookdev.shaders if item.shader_id and allowed and item.shader_id not in allowed}
    return result(USD_SHADER_IDS_ALLOWED, "Shader IDs Allowed", "Shaders", runtime_context, not invalid, f"Shaders using unapproved IDs: {len(invalid)}.", details={"shaders": invalid, "allowed": sorted(allowed)}, suggestion="Use a shader implementation approved by the profile.")


def check_shader_outputs_authored(context, runtime_context):
    required = runtime_context.config.shaders.require_outputs
    invalid = [item.path for item in context.lookdev.shaders if required and item.output_count == 0]
    return result(USD_SHADER_OUTPUTS_AUTHORED, "Shader Outputs Authored", "Shaders", runtime_context, not invalid, f"Shaders without outputs: {len(invalid)}.", details={"paths": invalid, "required": required}, suggestion="Author at least one shader output.")


def check_shader_asset_paths_relative(context, runtime_context):
    required = runtime_context.config.shaders.require_relative_asset_paths
    invalid = [path for item in context.lookdev.shaders for path in item.asset_inputs if required and os.path.isabs(path)]
    return result(USD_SHADER_ASSET_PATHS_RELATIVE, "Shader Asset Paths Relative", "Shaders", runtime_context, not invalid, f"Absolute shader asset paths: {len(invalid)}.", details={"paths": invalid, "required": required}, suggestion="Use portable relative texture and shader asset paths.")
