# rules/stage/checks.py

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
            layer=context.root_layer,
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
        suggestion="Verify that the file exists and contains valid OpenUSD data.",
    )]

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
            layer=context.root_layer,
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
        suggestion="Verify that the file exists and contains valid OpenUSD data.",
    )]


def check_stage_has_prims(context, runtime_context):
    if context.scene.total_prims > 0:
        return [CheckResult(
            check_id="USD_STAGE_HAS_PRIMS",
            label="Stage Has Prims",
            category="Stage",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message=f"The stage contains {context.scene.total_prims} prim(s).",
            details={
                "total_prims": context.scene.total_prims,
            },
        )]

    return [CheckResult(
        check_id="USD_STAGE_HAS_PRIMS",
        label="Stage Has Prims",
        category="Stage",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message="The USD Stage contains no prims.",
        suggestion="Add at least one scene prim before publishing.",
        details={
            "total_prims": context.scene.total_prims,
        },
    )]


def check_stage_has_root_prim(context, runtime_context):
    if context.scene.root_prims > 0:
        return [CheckResult(
            check_id="USD_STAGE_HAS_ROOT_PRIM",
            label="Stage Has Root Prim",
            category="Stage",
            status=CheckStatus.PASSED,
            severity=runtime_context.default_severity,
            message=f"The stage contains {context.scene.root_prims} root prim(s).",
            details={
                "root_prims": context.scene.root_prims,
            },
        )]

    return [CheckResult(
        check_id="USD_STAGE_HAS_ROOT_PRIM",
        label="Stage Has Root Prim",
        category="Stage",
        status=CheckStatus.FAILED,
        severity=runtime_context.default_severity,
        message="The USD Stage contains no root prims.",
        suggestion="Add at least one root prim to the stage before publishing.",
        details={
            "root_prims": context.scene.root_prims,
        },
    )]