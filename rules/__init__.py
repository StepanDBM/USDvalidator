from validation.registry import ValidationRegistry

from .stage import register_stage_checks
from .metadata import register_metadata_checks
from .composition import register_composition_checks
from .geometry import register_geometry_checks
from .animation import register_animation_checks


def build_registry():
    registry = ValidationRegistry()
    register_stage_checks(registry)
    register_metadata_checks(registry)
    register_composition_checks(registry)
    register_geometry_checks(registry)
    register_animation_checks(registry)
    return registry


__all__ = ["build_registry"]