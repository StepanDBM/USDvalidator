from contexts import StageHealthContext
from validation.enums import Severity
from validation.models import CheckDefinition

from .checks import (
    check_dependencies_resolve,
    check_payloads_resolve,
    check_references_resolve,
)

from validation.check_ids import (
    USD_DEPENDENCIES_RESOLVE,
    USD_REFERENCES_RESOLVE,
    USD_PAYLOADS_RESOLVE
)

def register_dependency_checks(registry):
    registry.register(CheckDefinition(
        check_id=USD_DEPENDENCIES_RESOLVE,
        label="USD Dependencies Resolve",
        description="Checks whether all referenced and payload USD dependencies resolve.",
        func=check_dependencies_resolve,
        target_type=StageHealthContext,
        category="Dependencies",
        phase="composition",
        default_severity=Severity.ERROR,
        tags=("dependencies", "composition", "publish", "required"),
    ))

    registry.register(CheckDefinition(
        check_id=USD_REFERENCES_RESOLVE,
        label="USD References Resolve",
        description="Checks whether all USD references resolve successfully.",
        func=check_references_resolve,
        target_type=StageHealthContext,
        category="Dependencies",
        phase="composition",
        default_severity=Severity.ERROR,
        tags=("dependencies", "references", "composition", "publish", "required"),
    ))

    registry.register(CheckDefinition(
        check_id=USD_PAYLOADS_RESOLVE,
        label="USD Payloads Resolve",
        description="Checks whether all USD payloads resolve successfully.",
        func=check_payloads_resolve,
        target_type=StageHealthContext,
        category="Dependencies",
        phase="composition",
        default_severity=Severity.ERROR,
        tags=("dependencies", "payloads", "composition", "publish", "required"),
    ))