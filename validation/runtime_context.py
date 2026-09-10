# validation/runtime_context.py

from dataclasses import dataclass

from .enums import Severity


@dataclass(frozen=True)
class CheckRuntimeContext:
    check_id: str
    default_severity: Severity