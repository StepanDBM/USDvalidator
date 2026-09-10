# rules/metadata/checks.py

from validation.enums import CheckStatus
from validation.models import CheckResult

def check_default_prim_authored(context, runtime_context):
    default_prim = context.stage.default_prim

    if default_prim:
        return [CheckResult(
            check_id="USD_DEFAULT_PRIM_AUTHORED",
            label="Default Prim Authored",
            category="Metadata",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message=f"The stage has an authored default prim: {default_prim}.",
            location=default_prim,
        )]

    return [CheckResult(
        check_id="USD_DEFAULT_PRIM_AUTHORED",
        label="Default Prim Authored",
        category="Metadata",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message="The stage does not have an authored default prim.",
        suggestion="Author a valid default prim before publishing.",
    )]


def check_default_prim_valid(context, runtime_context):
    default_prim_path = context.stage.default_prim

    if not default_prim_path:
        return [CheckResult(
            check_id="USD_DEFAULT_PRIM_VALID",
            label="Default Prim Valid",
            category="Metadata",
            status=CheckStatus.SKIPPED,
            severity=runtime_context.default_severity,
            message="No defaultPrim is authored; validity cannot be evaluated."
        )]

    if context.stage.default_prim_valid:
        return [CheckResult(
            check_id="USD_DEFAULT_PRIM_VALID",
            label="Default Prim Valid",
            category="Metadata",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message="The authored defaultPrim resolves to a valid prim.",
            location=default_prim_path,
            layer=context.stage.root_layer,
        )]

    return [CheckResult(
        check_id="USD_DEFAULT_PRIM_VALID",
        label="Default Prim Valid",
        category="Metadata",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message=(
            f"The authored defaultPrim '{default_prim_path}' "
            "does not resolve to a valid prim."
        ),
        location=default_prim_path,
        layer=context.stage.root_layer,
        suggestion="Set defaultPrim to the path of an existing valid prim."
    )]