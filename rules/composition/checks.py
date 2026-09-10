# rules/composition/checks.py

from validation.enums import CheckStatus
from validation.models import CheckResult


def check_no_unresolved_references(context, runtime_context):
    unresolved = context.composition.unresolved_references

    if unresolved == 0:
        return [CheckResult(
            check_id="USD_NO_UNRESOLVED_REFERENCES",
            label="No Unresolved References",
            category="Composition",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message="The stage contains no unresolved references.",
            details={
                "unresolved_references": unresolved,
            },
        )]

    return [CheckResult(
        check_id="USD_NO_UNRESOLVED_REFERENCES",
        label="No Unresolved References",
        category="Composition",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message=(
            f"The stage contains {unresolved} unresolved reference(s)."
        ),
        suggestion=(
            "Resolve all referenced asset paths before publishing."
        ),
        details={
            "unresolved_references": unresolved,
        },
    )]


def check_no_unresolved_payloads(context, runtime_context):
    unresolved = context.composition.unresolved_payloads

    if unresolved == 0:
        return [CheckResult(
            check_id="USD_NO_UNRESOLVED_PAYLOADS",
            label="No Unresolved Payloads",
            category="Composition",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message="The stage contains no unresolved payloads.",
            details={
                "unresolved_payloads": unresolved,
            },
        )]

    return [CheckResult(
        check_id="USD_NO_UNRESOLVED_PAYLOADS",
        label="No Unresolved Payloads",
        category="Composition",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message=(
            f"The stage contains {unresolved} unresolved payload(s)."
        ),
        suggestion=(
            "Resolve all payload asset paths before publishing."
        ),
        details={
            "unresolved_payloads": unresolved,
        },
    )]


def check_composition_layers_valid(context, runtime_context):
    invalid_layers = context.composition.invalid_layers

    if invalid_layers == 0:
        return [CheckResult(
            check_id="USD_COMPOSITION_LAYERS_VALID",
            label="Composition Layers Valid",
            category="Composition",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message="All composition layers are valid.",
            details={
                "invalid_layers": invalid_layers,
            },
        )]

    return [CheckResult(
        check_id="USD_COMPOSITION_LAYERS_VALID",
        label="Composition Layers Valid",
        category="Composition",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message=(
            f"The stage contains {invalid_layers} invalid composition layer(s)."
        ),
        suggestion=(
            "Verify that all referenced and sublayered USD files exist "
            "and can be opened."
        ),
        details={
            "invalid_layers": invalid_layers,
        },
    )]


def check_no_unexpected_arcs(context, runtime_context):
    unexpected_arcs = context.composition.unexpected_arcs

    if unexpected_arcs == 0:
        return [CheckResult(
            check_id="USD_NO_UNEXPECTED_ARCS",
            label="No Unexpected Composition Arcs",
            category="Composition",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message="The stage contains no unexpected composition arcs.",
            details={
                "unexpected_arcs": unexpected_arcs,
            },
        )]

    return [CheckResult(
        check_id="USD_NO_UNEXPECTED_ARCS",
        label="No Unexpected Composition Arcs",
        category="Composition",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message=(
            f"The stage contains {unexpected_arcs} unexpected "
            "composition arc(s)."
        ),
        suggestion=(
            "Review the stage composition and remove unintended "
            "references, payloads, variants, inherits, or specializes."
        ),
        details={
            "unexpected_arcs": unexpected_arcs,
        },
    )]