from dataclasses import dataclass

from .check_ids import (
    USD_ASSET_PATHS_RELATIVE,
    USD_FRAME_RANGE_LENGTH_LIMIT,
    USD_MESH_HAS_EXTENT,
    USD_MESH_POINT_COUNT_LIMIT,
    USD_MESH_POLYGON_COUNT_LIMIT,
    USD_METERS_PER_UNIT_VALID,
    USD_PAYLOAD_COUNT_LIMIT,
    USD_PAYLOADS_ALLOWED,
    USD_REFERENCE_COUNT_LIMIT,
    USD_ROOT_PRIM_NAME_VALID,
    USD_STAGE_MESH_COUNT_LIMIT,
    USD_STAGE_PRIM_COUNT_LIMIT,
    USD_STAGE_PRIM_DEPTH_LIMIT,
    USD_STAGE_TOTAL_POLYGON_COUNT_LIMIT,
    USD_TIME_SAMPLE_COUNT_LIMIT,
)


@dataclass(frozen=True)
class ConfigFieldDefinition:
    path: str
    label: str
    description: str
    value_type: type
    minimum: int | float | None = None
    maximum: int | float | None = None
    choices: tuple | None = None
    unit: str = ""
    related_check_ids: tuple[str, ...] = ()


FIELDS = (
    ConfigFieldDefinition("stage.prim_count_limit", "Stage Prim Count Limit", "Maximum number of prims allowed in the composed stage.", int, 1, 10000000, related_check_ids=(USD_STAGE_PRIM_COUNT_LIMIT,)),
    ConfigFieldDefinition("stage.prim_depth_limit", "Stage Prim Depth Limit", "Maximum hierarchy depth allowed below the pseudo-root.", int, 1, 1000, related_check_ids=(USD_STAGE_PRIM_DEPTH_LIMIT,)),
    ConfigFieldDefinition("geometry.polygon_count_limit", "Mesh Polygon Count Limit", "Maximum polygons allowed per mesh.", int, 1, 2147483647, related_check_ids=(USD_MESH_POLYGON_COUNT_LIMIT,)),
    ConfigFieldDefinition("geometry.point_count_limit", "Mesh Point Count Limit", "Maximum points allowed per mesh.", int, 1, 2147483647, related_check_ids=(USD_MESH_POINT_COUNT_LIMIT,)),
    ConfigFieldDefinition("geometry.total_polygon_count_limit", "Stage Total Polygon Count Limit", "Maximum total polygons allowed in the stage.", int, 1, 2147483647, related_check_ids=(USD_STAGE_TOTAL_POLYGON_COUNT_LIMIT,)),
    ConfigFieldDefinition("geometry.mesh_count_limit", "Stage Mesh Count Limit", "Maximum number of mesh prims allowed.", int, 0, 10000000, related_check_ids=(USD_STAGE_MESH_COUNT_LIMIT,)),
    ConfigFieldDefinition("geometry.require_extent", "Require Authored Mesh Extent", "Require every mesh to author its extent attribute.", bool, related_check_ids=(USD_MESH_HAS_EXTENT,)),
    ConfigFieldDefinition("metadata.minimum_meters_per_unit", "Minimum Meters Per Unit", "Smallest accepted stage scale.", float, 0.000000001, 1000.0, related_check_ids=(USD_METERS_PER_UNIT_VALID,)),
    ConfigFieldDefinition("metadata.maximum_meters_per_unit", "Maximum Meters Per Unit", "Largest accepted stage scale.", float, 0.000000001, 1000000.0, related_check_ids=(USD_METERS_PER_UNIT_VALID,)),
    ConfigFieldDefinition("metadata.required_root_prim_name", "Required Root Prim Name", "Required name of the default root prim.", str, related_check_ids=(USD_ROOT_PRIM_NAME_VALID,)),
    ConfigFieldDefinition("composition.reference_count_limit", "Reference Count Limit", "Maximum authored reference arcs.", int, 0, 1000000, related_check_ids=(USD_REFERENCE_COUNT_LIMIT,)),
    ConfigFieldDefinition("composition.payload_count_limit", "Payload Count Limit", "Maximum authored payload arcs.", int, 0, 1000000, related_check_ids=(USD_PAYLOAD_COUNT_LIMIT,)),
    ConfigFieldDefinition("composition.allow_payloads", "Allow Payloads", "Whether payload arcs are allowed in this profile.", bool, related_check_ids=(USD_PAYLOADS_ALLOWED,)),
    ConfigFieldDefinition("composition.require_relative_asset_paths", "Require Relative Asset Paths", "Reject absolute reference and payload paths.", bool, related_check_ids=(USD_ASSET_PATHS_RELATIVE,)),
    ConfigFieldDefinition("animation.maximum_frame_range", "Maximum Frame Range", "Maximum inclusive frame-range length.", int, 0, 10000000, unit="frames", related_check_ids=(USD_FRAME_RANGE_LENGTH_LIMIT,)),
    ConfigFieldDefinition("animation.maximum_time_samples", "Maximum Time Samples", "Maximum total authored time samples.", int, 0, 2147483647, related_check_ids=(USD_TIME_SAMPLE_COUNT_LIMIT,)),
)

CONFIG_FIELDS = {field.path: field for field in FIELDS}


def get_config_field(path):
    return CONFIG_FIELDS[path]


def get_config_fields():
    return FIELDS


def get_fields_for_check(check_id):
    return tuple(
        field for field in FIELDS if check_id in field.related_check_ids
    )
