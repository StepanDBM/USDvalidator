import re

from s_usd_core.rules.common import csv_values, result
from s_usd_core.validation.check_ids import (
    USD_FORBIDDEN_PRIM_NAMES,
    USD_PRIM_NAMES_MATCH_PATTERN,
    USD_PRIM_NAMES_NO_FORBIDDEN_TOKENS,
    USD_PRIM_NAMES_NO_WHITESPACE,
)


def _invalid(context, predicate):
    return [prim for prim in context.pipeline.prims if predicate(prim)]


def check_prim_names_no_whitespace(context, runtime_context):
    invalid = _invalid(context, lambda prim: any(char.isspace() for char in prim.name))
    return result(USD_PRIM_NAMES_NO_WHITESPACE, "Prim Names Have No Whitespace", "Naming", runtime_context, not invalid, f"Prim names containing whitespace: {len(invalid)}.", details={"paths": [item.path for item in invalid]}, suggestion="Rename prims to remove whitespace.")


def check_prim_names_no_forbidden_tokens(context, runtime_context):
    config = runtime_context.config.naming
    tokens = csv_values(config.forbidden_tokens_csv)
    normalized = tokens if config.case_sensitive else tuple(token.lower() for token in tokens)
    invalid = _invalid(context, lambda prim: any(token in (prim.name if config.case_sensitive else prim.name.lower()) for token in normalized))
    return result(USD_PRIM_NAMES_NO_FORBIDDEN_TOKENS, "Prim Names Have No Forbidden Tokens", "Naming", runtime_context, not invalid, f"Prim names containing forbidden tokens: {len(invalid)}.", details={"paths": [item.path for item in invalid], "tokens": list(tokens)}, suggestion="Rename temporary or placeholder prims.")


def check_prim_names_match_pattern(context, runtime_context):
    pattern = runtime_context.config.naming.prim_name_pattern
    regex = re.compile(pattern)
    invalid = _invalid(context, lambda prim: regex.fullmatch(prim.name) is None)
    return result(USD_PRIM_NAMES_MATCH_PATTERN, "Prim Names Match Pattern", "Naming", runtime_context, not invalid, f"Prim names outside the configured pattern: {len(invalid)}.", details={"paths": [item.path for item in invalid], "pattern": pattern}, suggestion="Rename prims to match the profile naming pattern.")


def check_forbidden_prim_names(context, runtime_context):
    config = runtime_context.config.naming
    names = csv_values(config.forbidden_names_csv)
    normalized = set(names if config.case_sensitive else (name.lower() for name in names))
    invalid = _invalid(context, lambda prim: (prim.name if config.case_sensitive else prim.name.lower()) in normalized)
    return result(USD_FORBIDDEN_PRIM_NAMES, "Forbidden Prim Names", "Naming", runtime_context, not invalid, f"Forbidden prim names found: {len(invalid)}.", details={"paths": [item.path for item in invalid], "forbidden_names": list(names)}, suggestion="Replace default DCC-generated names with publish names.")
