from s_usd_core.rules.common import result
from s_usd_core.validation.check_ids import (
    USD_MATRIX_XFORM_OPS_ALLOWED,
    USD_NEGATIVE_SCALE_ALLOWED,
    USD_ROOT_TRANSFORM_IDENTITY,
    USD_TRANSFORM_SCALE_NONZERO,
    USD_TRANSFORM_VALUES_FINITE,
    USD_XFORM_OP_COUNT_LIMIT,
)


def check_root_transform_identity(context, runtime_context):
    required = runtime_context.config.transforms.require_identity_root
    root = context.stage.default_prim
    item = next((value for value in context.pipeline.transforms if value.path == root), None)
    passed = not required or item is None or item.local_transform_identity
    return result(USD_ROOT_TRANSFORM_IDENTITY, "Root Transform Identity", "Transforms", runtime_context, passed, f"Root transform identity required: {required}.", location=root, details={"identity": item.local_transform_identity if item else None}, suggestion="Freeze or reset the root transform.")


def check_transform_values_finite(context, runtime_context):
    invalid = [item.path for item in context.pipeline.transforms if not item.values_finite]
    return result(USD_TRANSFORM_VALUES_FINITE, "Transform Values Finite", "Transforms", runtime_context, not invalid, f"Transforms containing NaN or infinity: {len(invalid)}.", details={"paths": invalid}, suggestion="Replace non-finite transform values.")


def check_transform_scale_nonzero(context, runtime_context):
    tolerance = runtime_context.config.transforms.zero_scale_tolerance
    invalid = [item.path for item in context.pipeline.transforms if any(abs(component) <= tolerance for scale in item.scale_values for component in scale)]
    return result(USD_TRANSFORM_SCALE_NONZERO, "Transform Scale Nonzero", "Transforms", runtime_context, not invalid, f"Transforms containing zero scale: {len(invalid)}.", details={"paths": invalid, "tolerance": tolerance}, suggestion="Use nonzero scale values.")


def check_negative_scale_allowed(context, runtime_context):
    allowed = runtime_context.config.transforms.allow_negative_scale
    invalid = [item.path for item in context.pipeline.transforms if not allowed and any(component < 0 for scale in item.scale_values for component in scale)]
    return result(USD_NEGATIVE_SCALE_ALLOWED, "Negative Scale Policy", "Transforms", runtime_context, not invalid, f"Transforms using forbidden negative scale: {len(invalid)}.", details={"paths": invalid, "allowed": allowed}, suggestion="Remove negative scale or allow it in the profile.")


def check_xform_op_count_limit(context, runtime_context):
    limit = runtime_context.config.transforms.maximum_xform_ops
    invalid = [item.path for item in context.pipeline.transforms if len(item.op_names) > limit]
    return result(USD_XFORM_OP_COUNT_LIMIT, "Xform Op Count Limit", "Transforms", runtime_context, not invalid, f"Transforms exceeding {limit} xform ops: {len(invalid)}.", details={"paths": invalid, "limit": limit}, suggestion="Simplify transform operation stacks.")


def check_matrix_xform_ops_allowed(context, runtime_context):
    allowed = runtime_context.config.transforms.allow_matrix_ops
    invalid = [item.path for item in context.pipeline.transforms if not allowed and item.matrix_op_count > 0]
    return result(USD_MATRIX_XFORM_OPS_ALLOWED, "Matrix Xform Ops Allowed", "Transforms", runtime_context, not invalid, f"Transforms using forbidden matrix ops: {len(invalid)}.", details={"paths": invalid, "allowed": allowed}, suggestion="Author explicit TRS operations or allow matrix ops.")
