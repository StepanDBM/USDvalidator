from rules.common import result
from validation.check_ids import (
    USD_GEOMETRY_HAS_MATERIAL_BINDING,
    USD_MATERIAL_BINDINGS_RESOLVE,
    USD_MATERIAL_COUNT_LIMIT,
    USD_MATERIAL_SURFACE_OUTPUT_CONNECTED,
    USD_MATERIALS_UNDER_REQUIRED_SCOPE,
)


def check_material_count_limit(context, runtime_context):
    count = len(context.lookdev.materials)
    limit = runtime_context.config.materials.maximum_count
    return result(USD_MATERIAL_COUNT_LIMIT, "Material Count Limit", "Materials", runtime_context, count <= limit, f"Material count {count}; allowed maximum {limit}.", details={"count": count, "limit": limit})


def check_material_surface_output_connected(context, runtime_context):
    required = runtime_context.config.materials.require_surface_output
    invalid = [item.path for item in context.lookdev.materials if required and not item.surface_connected]
    return result(USD_MATERIAL_SURFACE_OUTPUT_CONNECTED, "Material Surface Output Connected", "Materials", runtime_context, not invalid, f"Materials without connected surface outputs: {len(invalid)}.", details={"paths": invalid, "required": required}, suggestion="Connect a shader output to the material surface output.")


def check_geometry_has_material_binding(context, runtime_context):
    required = runtime_context.config.materials.require_bindings_on_meshes
    bound = {item.prim_path for item in context.lookdev.bindings if item.resolved}
    invalid = [item.mesh_path for item in context.lookdev.surfaces if required and item.mesh_path not in bound]
    return result(USD_GEOMETRY_HAS_MATERIAL_BINDING, "Geometry Has Material Binding", "Materials", runtime_context, not invalid, f"Meshes without resolved material bindings: {len(invalid)}.", details={"paths": invalid, "required": required}, suggestion="Bind a valid material to each required mesh.")


def check_material_bindings_resolve(context, runtime_context):
    invalid = [item.prim_path for item in context.lookdev.bindings if not item.resolved]
    return result(USD_MATERIAL_BINDINGS_RESOLVE, "Material Bindings Resolve", "Materials", runtime_context, not invalid, f"Unresolved material bindings: {len(invalid)}.", details={"paths": invalid}, suggestion="Repair material binding targets.")


def check_materials_under_required_scope(context, runtime_context):
    config = runtime_context.config.materials
    root = config.required_scope_path.rstrip("/")
    invalid = [item.path for item in context.lookdev.materials if config.require_materials_under_scope and not item.path.startswith(root + "/")]
    return result(USD_MATERIALS_UNDER_REQUIRED_SCOPE, "Materials Under Required Scope", "Materials", runtime_context, not invalid, f"Materials outside {root}: {len(invalid)}.", details={"paths": invalid, "required_scope": root}, suggestion="Move materials beneath the configured material scope.")
