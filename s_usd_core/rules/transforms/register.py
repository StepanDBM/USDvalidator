from s_usd_core.contexts import StageHealthContext
from s_usd_core.validation.check_ids import (
    USD_ROOT_TRANSFORM_IDENTITY,
    USD_TRANSFORM_VALUES_FINITE,
    USD_TRANSFORM_SCALE_NONZERO,
    USD_NEGATIVE_SCALE_ALLOWED,
    USD_XFORM_OP_COUNT_LIMIT,
    USD_MATRIX_XFORM_OPS_ALLOWED,
)
from s_usd_core.validation.enums import Severity
from s_usd_core.validation.models import CheckDefinition

from .checks import (
    check_root_transform_identity,
    check_transform_values_finite,
    check_transform_scale_nonzero,
    check_negative_scale_allowed,
    check_xform_op_count_limit,
    check_matrix_xform_ops_allowed,
)


def register_transforms_checks(registry):
    entries = (
        (USD_ROOT_TRANSFORM_IDENTITY, "Root Transform Identity", check_root_transform_identity, Severity.WARNING),
        (USD_TRANSFORM_VALUES_FINITE, "Transform Values Finite", check_transform_values_finite, Severity.ERROR),
        (USD_TRANSFORM_SCALE_NONZERO, "Transform Scale Nonzero", check_transform_scale_nonzero, Severity.ERROR),
        (USD_NEGATIVE_SCALE_ALLOWED, "Negative Scale Policy", check_negative_scale_allowed, Severity.WARNING),
        (USD_XFORM_OP_COUNT_LIMIT, "Xform Op Count Limit", check_xform_op_count_limit, Severity.WARNING),
        (USD_MATRIX_XFORM_OPS_ALLOWED, "Matrix Xform Ops Allowed", check_matrix_xform_ops_allowed, Severity.WARNING),
    )

    for check_id, label, func, severity in entries:
        registry.register(CheckDefinition(
            check_id=check_id,
            label=label,
            description=label,
            func=func,
            target_type=StageHealthContext,
            category="Transforms",
            phase="structure",
            default_severity=severity,
            tags=("transforms", "publish"),
        ))
