# rules/composition/checks.py

from validation.check_ids import *
from validation.enums import CheckStatus
from validation.models import CheckResult

def _result(check_id, label, category, runtime, passed, message, details=None, suggestion=""):
    return [CheckResult(
        check_id=check_id, label=label, category=category,
        status=CheckStatus.PASSED if passed else CheckStatus.FAILED,
        severity=runtime.default_severity, message=message,
        suggestion=suggestion, details=details or {},
    )]


def check_no_unresolved_references(context, runtime_context):
    count = context.composition.unresolved_references
    return _result(USD_NO_UNRESOLVED_REFERENCES, "No Unresolved References", "Composition", runtime_context, count == 0, f"Unresolved references: {count}.", {"count": count}, "Resolve all reference paths.")

def check_no_unresolved_payloads(context, runtime_context):
    count = context.composition.unresolved_payloads
    return _result(USD_NO_UNRESOLVED_PAYLOADS, "No Unresolved Payloads", "Composition", runtime_context, count == 0, f"Unresolved payloads: {count}.", {"count": count}, "Resolve all payload paths.")

def check_composition_layers_valid(context, runtime_context):
    count = context.composition.invalid_layers
    return _result(USD_COMPOSITION_LAYERS_VALID, "Composition Layers Valid", "Composition", runtime_context, count == 0, f"Invalid layers: {count}.", {"count": count}, "Repair invalid layers.")

def check_no_unexpected_arcs(context, runtime_context):
    count = context.composition.unexpected_arcs
    return _result(USD_NO_UNEXPECTED_ARCS, "No Unexpected Composition Arcs", "Composition", runtime_context, count == 0, f"Unexpected composition errors: {count}.", {"count": count}, "Review composition errors.")

def check_reference_count_limit(context, runtime_context):
    count = context.composition.references
    limit = runtime_context.config.composition.reference_count_limit
    return _result(USD_REFERENCE_COUNT_LIMIT, "Reference Count Limit", "Composition", runtime_context, count <= limit, f"References {count}; allowed maximum {limit}.", {"count": count, "limit": limit}, "Reduce reference count or override the limit.")

def check_payload_count_limit(context, runtime_context):
    count = context.composition.payloads
    limit = runtime_context.config.composition.payload_count_limit
    return _result(USD_PAYLOAD_COUNT_LIMIT, "Payload Count Limit", "Composition", runtime_context, count <= limit, f"Payloads {count}; allowed maximum {limit}.", {"count": count, "limit": limit}, "Reduce payload count or override the limit.")

def check_payloads_allowed(context, runtime_context):
    count = context.composition.payloads
    allowed = runtime_context.config.composition.allow_payloads
    return _result(USD_PAYLOADS_ALLOWED, "Payloads Allowed", "Composition", runtime_context, allowed or count == 0, f"Stage contains {count} payload(s); profile allows payloads: {allowed}.", {"count": count, "allowed": allowed}, "Remove payloads or enable them in the profile.")

def check_asset_paths_relative(context, runtime_context):
    paths = context.composition.absolute_asset_paths
    required = runtime_context.config.composition.require_relative_asset_paths
    return _result(USD_ASSET_PATHS_RELATIVE, "Asset Paths Relative", "Composition", runtime_context, not required or not paths, f"Absolute asset paths: {len(paths)}.", {"paths": paths}, "Author relative asset paths for portable publishes.")
