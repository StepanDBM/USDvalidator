from contexts import StageHealthContext
from validation.check_ids import (
    USD_LAYER_COUNT_LIMIT,
    USD_NO_ANONYMOUS_LAYERS,
    USD_NO_DIRTY_LAYERS,
    USD_SUBLAYER_COUNT_LIMIT,
    USD_ROOT_LAYER_DEFAULT_PRIM_AUTHORED,
)
from validation.enums import Severity
from validation.models import CheckDefinition

from .checks import (
    check_layer_count_limit,
    check_no_anonymous_layers,
    check_no_dirty_layers,
    check_sublayer_count_limit,
    check_root_layer_default_prim_authored,
)


def register_layers_checks(registry):
    entries = (
        (USD_LAYER_COUNT_LIMIT, "Layer Count Limit", check_layer_count_limit, Severity.WARNING),
        (USD_NO_ANONYMOUS_LAYERS, "No Anonymous Layers", check_no_anonymous_layers, Severity.ERROR),
        (USD_NO_DIRTY_LAYERS, "No Dirty Layers", check_no_dirty_layers, Severity.WARNING),
        (USD_SUBLAYER_COUNT_LIMIT, "Sublayer Count Limit", check_sublayer_count_limit, Severity.WARNING),
        (USD_ROOT_LAYER_DEFAULT_PRIM_AUTHORED, "Root Layer Default Prim Authored", check_root_layer_default_prim_authored, Severity.ERROR),
    )

    for check_id, label, func, severity in entries:
        registry.register(CheckDefinition(
            check_id=check_id,
            label=label,
            description=label,
            func=func,
            target_type=StageHealthContext,
            category="Layers",
            phase="composition",
            default_severity=severity,
            tags=("layers", "publish"),
        ))
