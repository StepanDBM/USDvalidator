from s_usd_core.validation.registry import ValidationRegistry

from .stage import register_stage_checks
from .metadata import register_metadata_checks
from .composition import register_composition_checks
from .geometry import register_geometry_checks
from .animation import register_animation_checks
from .dependencies import register_dependency_checks
from .naming import register_naming_checks
from .hierarchy import register_hierarchy_checks
from .transforms import register_transforms_checks
from .variants import register_variants_checks
from .cameras import register_cameras_checks
from .instancing import register_instancing_checks
from .packaging import register_packaging_checks
from .layers import register_layers_checks
from .uvs import register_uvs_checks
from .normals import register_normals_checks
from .shaders import register_shaders_checks
from .materials import register_materials_checks


def build_registry():
    registry = ValidationRegistry()
    register_stage_checks(registry)
    register_metadata_checks(registry)
    register_composition_checks(registry)
    register_geometry_checks(registry)
    register_animation_checks(registry)
    register_dependency_checks(registry)
    register_naming_checks(registry)
    register_hierarchy_checks(registry)
    register_transforms_checks(registry)
    register_variants_checks(registry)
    register_cameras_checks(registry)
    register_instancing_checks(registry)
    register_packaging_checks(registry)
    register_layers_checks(registry)
    register_uvs_checks(registry)
    register_normals_checks(registry)
    register_shaders_checks(registry)
    register_materials_checks(registry)
    return registry


__all__ = ["build_registry"]