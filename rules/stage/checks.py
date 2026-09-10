# rules/stage/checks.py

from contexts import StageHealthContext
from validation.enums import CheckStatus
from validation.models import CheckResult

def check_stage_can_open(context, runtime_context):
    if context.opened:
        return [CheckResult(
            check_id="USD_STAGE_CAN_OPEN",
            label="Stage Can Open",
            category="Stage",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message="The USD Stage opened successfully.",
            location=context.source_path,
            layer=context.root_layer
        )]

    message = context.error_message or "The USD Stage could not be opened."

    return [CheckResult(
        check_id="USD_STAGE_CAN_OPEN",
        label="Stage Can Open",
        category="Stage",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message=message,
        location=context.source_path,
        suggestion="Verify that the file exists and contains valid OpenUSD data."
    )]

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