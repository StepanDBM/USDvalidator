from s_usd_core.contexts import StageHealthContext
from s_usd_core.validation.check_ids import (
    USD_REQUIRED_VARIANT_SETS_EXIST,
    USD_VARIANT_SELECTIONS_AUTHORED,
    USD_VARIANT_SELECTIONS_VALID,
    USD_VARIANT_SET_COUNT_LIMIT,
)
from s_usd_core.validation.enums import Severity
from s_usd_core.validation.models import CheckDefinition

from .checks import (
    check_required_variant_sets_exist,
    check_variant_selections_authored,
    check_variant_selections_valid,
    check_variant_set_count_limit,
)


def register_variants_checks(registry):
    entries = (
        (USD_REQUIRED_VARIANT_SETS_EXIST, "Required Variant Sets Exist", check_required_variant_sets_exist, Severity.ERROR),
        (USD_VARIANT_SELECTIONS_AUTHORED, "Variant Selections Authored", check_variant_selections_authored, Severity.WARNING),
        (USD_VARIANT_SELECTIONS_VALID, "Variant Selections Valid", check_variant_selections_valid, Severity.ERROR),
        (USD_VARIANT_SET_COUNT_LIMIT, "Variant Set Count Limit", check_variant_set_count_limit, Severity.WARNING),
    )

    for check_id, label, func, severity in entries:
        registry.register(CheckDefinition(
            check_id=check_id,
            label=label,
            description=label,
            func=func,
            target_type=StageHealthContext,
            category="Variants",
            phase="composition",
            default_severity=severity,
            tags=("variants", "publish"),
        ))
