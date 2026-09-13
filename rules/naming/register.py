from contexts import StageHealthContext
from validation.check_ids import (
    USD_PRIM_NAMES_NO_WHITESPACE,
    USD_PRIM_NAMES_NO_FORBIDDEN_TOKENS,
    USD_PRIM_NAMES_MATCH_PATTERN,
    USD_FORBIDDEN_PRIM_NAMES,
)
from validation.enums import Severity
from validation.models import CheckDefinition

from .checks import (
    check_prim_names_no_whitespace,
    check_prim_names_no_forbidden_tokens,
    check_prim_names_match_pattern,
    check_forbidden_prim_names,
)


def register_naming_checks(registry):
    entries = (
        (USD_PRIM_NAMES_NO_WHITESPACE, "Prim Names Have No Whitespace", check_prim_names_no_whitespace, Severity.ERROR),
        (USD_PRIM_NAMES_NO_FORBIDDEN_TOKENS, "Prim Names Have No Forbidden Tokens", check_prim_names_no_forbidden_tokens, Severity.WARNING),
        (USD_PRIM_NAMES_MATCH_PATTERN, "Prim Names Match Pattern", check_prim_names_match_pattern, Severity.ERROR),
        (USD_FORBIDDEN_PRIM_NAMES, "Forbidden Prim Names", check_forbidden_prim_names, Severity.WARNING),
    )

    for check_id, label, func, severity in entries:
        registry.register(CheckDefinition(
            check_id=check_id,
            label=label,
            description=label,
            func=func,
            target_type=StageHealthContext,
            category="Naming",
            phase="structure",
            default_severity=severity,
            tags=("naming", "publish"),
        ))
