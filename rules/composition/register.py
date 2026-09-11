# rules/composition/register.py

from contexts import StageHealthContext
from validation.enums import Severity
from validation.models import CheckDefinition

from .checks import (
    check_no_unresolved_references,
    check_no_unresolved_payloads,
    check_composition_layers_valid,
    check_no_unexpected_arcs,
)

from validation.check_ids import (
    USD_NO_UNRESOLVED_REFERENCES,
    USD_NO_UNRESOLVED_PAYLOADS,
    USD_COMPOSITION_LAYERS_VALID,
    USD_NO_UNEXPECTED_ARCS
)


def register_composition_checks(registry):
    registry.register(CheckDefinition(
        check_id=USD_NO_UNRESOLVED_REFERENCES,
        label="No Unresolved References",
        description="Checks whether the stage contains unresolved references.",
        func=check_no_unresolved_references,
        target_type=StageHealthContext,
        category="Composition",
        phase="composition",
        default_severity=Severity.ERROR,
        tags=("composition", "references", "publish", "required"),
    ))

    registry.register(CheckDefinition(
        check_id=USD_NO_UNRESOLVED_PAYLOADS,
        label="No Unresolved Payloads",
        description="Checks whether the stage contains unresolved payloads.",
        func=check_no_unresolved_payloads,
        target_type=StageHealthContext,
        category="Composition",
        phase="composition",
        default_severity=Severity.ERROR,
        tags=("composition", "payloads", "publish", "required"),
    ))

    registry.register(CheckDefinition(
        check_id=USD_COMPOSITION_LAYERS_VALID,
        label="Composition Layers Valid",
        description="Checks whether all composition layers are valid.",
        func=check_composition_layers_valid,
        target_type=StageHealthContext,
        category="Composition",
        phase="composition",
        default_severity=Severity.ERROR,
        tags=("composition", "layers", "publish", "required"),
    ))

    registry.register(CheckDefinition(
        check_id=USD_NO_UNEXPECTED_ARCS,
        label="No Unexpected Composition Arcs",
        description="Checks whether the stage contains unexpected composition arcs.",
        func=check_no_unexpected_arcs,
        target_type=StageHealthContext,
        category="Composition",
        phase="composition",
        default_severity=Severity.ERROR,
        tags=("composition", "arcs", "publish", "required"),
    ))