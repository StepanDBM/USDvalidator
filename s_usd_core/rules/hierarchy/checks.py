from s_usd_core.rules.common import csv_values, result
from s_usd_core.validation.check_ids import (
    USD_MESHES_UNDER_REQUIRED_SCOPE,
    USD_NO_MESHES_AT_PSEUDO_ROOT,
    USD_REQUIRED_HIERARCHY_PATHS_EXIST,
    USD_SINGLE_ROOT_PRIM_REQUIRED,
)


def check_single_root_prim_required(context, runtime_context):
    count = context.scene.root_prims
    required = runtime_context.config.hierarchy.require_single_root
    passed = not required or count == 1
    return result(USD_SINGLE_ROOT_PRIM_REQUIRED, "Single Root Prim Required", "Hierarchy", runtime_context, passed, f"Root prim count: {count}; single root required: {required}.", details={"root_prims": count, "required": required}, suggestion="Consolidate the publish under one root prim.")


def check_required_hierarchy_paths_exist(context, runtime_context):
    required = csv_values(
        runtime_context.config.hierarchy.required_paths_csv
    )

    if not required:
        return result(
            USD_REQUIRED_HIERARCHY_PATHS_EXIST,
            "Required Hierarchy Paths Exist",
            "Hierarchy",
            runtime_context,
            True,
            "No required hierarchy paths are configured.",
            details={
                "required_paths": [],
                "missing_paths": [],
                "enforced": False,
            },
        )

    existing = {prim.path for prim in context.pipeline.prims}
    missing = [path for path in required if path not in existing]

    return result(
        USD_REQUIRED_HIERARCHY_PATHS_EXIST,
        "Required Hierarchy Paths Exist",
        "Hierarchy",
        runtime_context,
        not missing,
        (
            f"Required hierarchy paths: {len(required)}; "
            f"missing: {len(missing)}."
        ),
        details={
            "required_paths": list(required),
            "missing_paths": missing,
            "enforced": True,
        },
        suggestion=(
            "Author the configured hierarchy paths or remove the path "
            "requirements from this validation profile."
        ),
    )

def check_meshes_under_required_scope(context, runtime_context):
    config = runtime_context.config.hierarchy
    root = config.geometry_root_path.rstrip("/")
    invalid = [prim.path for prim in context.pipeline.prims if prim.type_name == "Mesh" and config.require_meshes_under_geometry_root and not prim.path.startswith(root + "/")]
    return result(USD_MESHES_UNDER_REQUIRED_SCOPE, "Meshes Under Required Scope", "Hierarchy", runtime_context, not invalid, f"Meshes outside {root}: {len(invalid)}.", details={"paths": invalid, "geometry_root": root}, suggestion="Parent mesh prims below the configured geometry root.")


def check_no_meshes_at_pseudo_root(context, runtime_context):
    invalid = [prim.path for prim in context.pipeline.prims if prim.type_name == "Mesh" and prim.depth == 1]
    return result(USD_NO_MESHES_AT_PSEUDO_ROOT, "No Meshes At Pseudo Root", "Hierarchy", runtime_context, not invalid, f"Mesh prims directly below the pseudo-root: {len(invalid)}.", details={"paths": invalid}, suggestion="Place geometry under an asset or world root prim.")
