from validation.registry import ValidationRegistry

from .stage import register_stage_checks


def build_registry():
    registry = ValidationRegistry()
    register_stage_checks(registry)
    return registry


__all__ = ["build_registry"]