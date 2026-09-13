from validation.check_ids import (
    USD_STAGE_CAN_OPEN, USD_STAGE_HAS_PRIMS, USD_STAGE_HAS_ROOT_PRIM,
    USD_STAGE_PRIM_COUNT_LIMIT, USD_STAGE_PRIM_DEPTH_LIMIT,
)
from validation.enums import CheckStatus
from validation.models import CheckResult

def _result(check_id, label, category, runtime, passed, message, details=None, suggestion=""):
    return [CheckResult(
        check_id=check_id,
        label=label,
        category=category,
        status=CheckStatus.PASSED if passed else CheckStatus.FAILED,
        severity=runtime.default_severity,
        message=message,
        suggestion=suggestion,
        details=details or {},
    )]


def check_stage_can_open(context, runtime_context):
    return _result(
        USD_STAGE_CAN_OPEN, "Stage Can Open", "Stage", runtime_context,
        context.opened, "The USD stage opened successfully." if context.opened
        else f"The USD stage could not be opened: {context.error_message}",
    )


def check_stage_has_prims(context, runtime_context):
    count = context.scene.total_prims
    return _result(
        USD_STAGE_HAS_PRIMS, "Stage Has Prims", "Stage", runtime_context,
        count > 0, f"The stage contains {count} prim(s).",
        {"total_prims": count}, "Author at least one prim before publishing.",
    )


def check_stage_has_root_prim(context, runtime_context):
    count = context.scene.root_prims
    return _result(
        USD_STAGE_HAS_ROOT_PRIM, "Stage Has Root Prim", "Stage", runtime_context,
        count > 0, f"The stage contains {count} root prim(s).",
        {"root_prims": count}, "Author a root prim before publishing.",
    )


def check_stage_prim_count_limit(context, runtime_context):
    count = context.scene.total_prims
    limit = runtime_context.config.stage.prim_count_limit
    return _result(
        USD_STAGE_PRIM_COUNT_LIMIT, "Stage Prim Count Limit", "Stage", runtime_context,
        count <= limit, f"Stage prim count {count}; allowed maximum {limit}.",
        {"total_prims": count, "limit": limit}, "Reduce stage hierarchy complexity.",
    )


def check_stage_prim_depth_limit(context, runtime_context):
    depth = context.scene.maximum_prim_depth
    limit = runtime_context.config.stage.prim_depth_limit
    return _result(
        USD_STAGE_PRIM_DEPTH_LIMIT, "Stage Prim Depth Limit", "Stage", runtime_context,
        depth <= limit, f"Maximum prim depth {depth}; allowed maximum {limit}.",
        {"maximum_prim_depth": depth, "limit": limit}, "Flatten or simplify deep hierarchy branches.",
    )
