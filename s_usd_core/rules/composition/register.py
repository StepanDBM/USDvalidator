# rules/composition/register.py

from s_usd_core.contexts import StageHealthContext
from s_usd_core.validation.check_ids import *
from s_usd_core.validation.enums import Severity
from s_usd_core.validation.models import CheckDefinition
from .checks import *


def register_composition_checks(registry):
    entries = (
        (USD_NO_UNRESOLVED_REFERENCES, "No Unresolved References", check_no_unresolved_references, Severity.ERROR, ("composition", "references", "required")),
        (USD_NO_UNRESOLVED_PAYLOADS, "No Unresolved Payloads", check_no_unresolved_payloads, Severity.ERROR, ("composition", "payloads", "required")),
        (USD_COMPOSITION_LAYERS_VALID, "Composition Layers Valid", check_composition_layers_valid, Severity.ERROR, ("composition", "layers")),
        (USD_NO_UNEXPECTED_ARCS, "No Unexpected Composition Arcs", check_no_unexpected_arcs, Severity.ERROR, ("composition", "arcs")),
        (USD_REFERENCE_COUNT_LIMIT, "Reference Count Limit", check_reference_count_limit, Severity.WARNING, ("composition", "references", "budget")),
        (USD_PAYLOAD_COUNT_LIMIT, "Payload Count Limit", check_payload_count_limit, Severity.WARNING, ("composition", "payloads", "budget")),
        (USD_PAYLOADS_ALLOWED, "Payloads Allowed", check_payloads_allowed, Severity.ERROR, ("composition", "payloads", "policy")),
        (USD_ASSET_PATHS_RELATIVE, "Asset Paths Relative", check_asset_paths_relative, Severity.ERROR, ("composition", "assets", "portability")),
    )
    for check_id, label, func, severity, tags in entries:
        registry.register(CheckDefinition(check_id=check_id, label=label, description=label, func=func, target_type=StageHealthContext, category="Composition", phase="composition", default_severity=severity, tags=tags))
