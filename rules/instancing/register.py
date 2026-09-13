from contexts import StageHealthContext
from validation.check_ids import (
    USD_INSTANCE_COUNT_LIMIT,
    USD_POINT_INSTANCE_COUNT_LIMIT,
    USD_POINT_INSTANCER_PROTOTYPES_VALID,
    USD_POINT_INSTANCER_INDICES_VALID,
    USD_INSTANCE_PROTOTYPES_VALID,
)
from validation.enums import Severity
from validation.models import CheckDefinition

from .checks import (
    check_instance_count_limit,
    check_point_instance_count_limit,
    check_point_instancer_prototypes_valid,
    check_point_instancer_indices_valid,
    check_instance_prototypes_valid,
)


def register_instancing_checks(registry):
    entries = (
        (USD_INSTANCE_COUNT_LIMIT, "Instance Count Limit", check_instance_count_limit, Severity.WARNING),
        (USD_POINT_INSTANCE_COUNT_LIMIT, "Point Instance Count Limit", check_point_instance_count_limit, Severity.WARNING),
        (USD_POINT_INSTANCER_PROTOTYPES_VALID, "Point Instancer Prototypes Valid", check_point_instancer_prototypes_valid, Severity.ERROR),
        (USD_POINT_INSTANCER_INDICES_VALID, "Point Instancer Indices Valid", check_point_instancer_indices_valid, Severity.ERROR),
        (USD_INSTANCE_PROTOTYPES_VALID, "Instance Prototypes Valid", check_instance_prototypes_valid, Severity.ERROR),
    )

    for check_id, label, func, severity in entries:
        registry.register(CheckDefinition(
            check_id=check_id,
            label=label,
            description=label,
            func=func,
            target_type=StageHealthContext,
            category="Instancing",
            phase="performance",
            default_severity=severity,
            tags=("instancing", "publish"),
        ))
