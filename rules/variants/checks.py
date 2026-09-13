from rules.common import csv_values, result
from validation.check_ids import (
    USD_REQUIRED_VARIANT_SETS_EXIST,
    USD_VARIANT_SELECTIONS_AUTHORED,
    USD_VARIANT_SELECTIONS_VALID,
    USD_VARIANT_SET_COUNT_LIMIT,
)


def check_required_variant_sets_exist(context, runtime_context):
    required = csv_values(runtime_context.config.variants.required_sets_csv)
    existing = {item.name for item in context.pipeline.variants}
    missing = [name for name in required if name not in existing]
    return result(USD_REQUIRED_VARIANT_SETS_EXIST, "Required Variant Sets Exist", "Variants", runtime_context, not missing, f"Missing required variant sets: {len(missing)}.", details={"missing": missing, "required": list(required)}, suggestion="Author the required variant sets.")


def check_variant_selections_authored(context, runtime_context):
    required = runtime_context.config.variants.require_authored_selections
    invalid = [f"{item.prim_path}:{item.name}" for item in context.pipeline.variants if required and not item.selection]
    return result(USD_VARIANT_SELECTIONS_AUTHORED, "Variant Selections Authored", "Variants", runtime_context, not invalid, f"Variant sets without authored selections: {len(invalid)}.", details={"variant_sets": invalid, "required": required}, suggestion="Author a default selection for each variant set.")


def check_variant_selections_valid(context, runtime_context):
    invalid = [f"{item.prim_path}:{item.name}={item.selection}" for item in context.pipeline.variants if item.selection and item.selection not in item.variants]
    return result(USD_VARIANT_SELECTIONS_VALID, "Variant Selections Valid", "Variants", runtime_context, not invalid, f"Invalid variant selections: {len(invalid)}.", details={"variant_sets": invalid}, suggestion="Select an option that exists in the variant set.")


def check_variant_set_count_limit(context, runtime_context):
    limit = runtime_context.config.variants.maximum_sets_per_prim
    counts = {}
    for item in context.pipeline.variants:
        counts[item.prim_path] = counts.get(item.prim_path, 0) + 1
    invalid = {path: count for path, count in counts.items() if count > limit}
    return result(USD_VARIANT_SET_COUNT_LIMIT, "Variant Set Count Limit", "Variants", runtime_context, not invalid, f"Prims exceeding {limit} variant sets: {len(invalid)}.", details={"prims": invalid, "limit": limit}, suggestion="Reduce variant-set complexity or override the limit.")
