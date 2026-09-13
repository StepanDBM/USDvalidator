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

# Additional profile-editable fields for pipeline domains.
from .check_ids import (
    USD_CAMERA_ANIMATION_ALLOWED,
    USD_CAMERA_CLIPPING_RANGE_VALID,
    USD_CAMERA_COUNT_LIMIT,
    USD_CAMERA_FOCAL_LENGTH_VALID,
    USD_CAMERA_REQUIRED,
    USD_DEPENDENCY_COUNT_LIMIT,
    USD_FORBIDDEN_PRIM_NAMES,
    USD_INSTANCE_COUNT_LIMIT,
    USD_MATRIX_XFORM_OPS_ALLOWED,
    USD_MESHES_UNDER_REQUIRED_SCOPE,
    USD_NEGATIVE_SCALE_ALLOWED,
    USD_NO_ABSOLUTE_DEPENDENCY_PATHS,
    USD_NO_PARENT_DIRECTORY_ESCAPES,
    USD_NO_TEMPORARY_DEPENDENCIES,
    USD_PRIM_NAMES_MATCH_PATTERN,
    USD_PRIM_NAMES_NO_FORBIDDEN_TOKENS,
    USD_RENDER_CAMERA_EXISTS,
    USD_REQUIRED_HIERARCHY_PATHS_EXIST,
    USD_REQUIRED_VARIANT_SETS_EXIST,
    USD_ROOT_TRANSFORM_IDENTITY,
    USD_SINGLE_ROOT_PRIM_REQUIRED,
    USD_SOURCE_EXTENSION_ALLOWED,
    USD_SOURCE_FILENAME_VALID,
    USD_TRANSFORM_SCALE_NONZERO,
    USD_VARIANT_SELECTIONS_AUTHORED,
    USD_VARIANT_SET_COUNT_LIMIT,
    USD_XFORM_OP_COUNT_LIMIT,
    USD_POINT_INSTANCE_COUNT_LIMIT,
    USD_POINT_INSTANCER_PROTOTYPES_VALID,
)

ADDITIONAL_FIELDS = (
    ConfigFieldDefinition("naming.prim_name_pattern", "Prim Name Pattern", "Regular expression required for all prim names.", str, related_check_ids=(USD_PRIM_NAMES_MATCH_PATTERN,)),
    ConfigFieldDefinition("naming.forbidden_tokens_csv", "Forbidden Name Tokens", "Comma-separated tokens forbidden inside prim names.", str, related_check_ids=(USD_PRIM_NAMES_NO_FORBIDDEN_TOKENS,)),
    ConfigFieldDefinition("naming.forbidden_names_csv", "Forbidden Prim Names", "Comma-separated exact prim names forbidden by the profile.", str, related_check_ids=(USD_FORBIDDEN_PRIM_NAMES,)),
    ConfigFieldDefinition("naming.case_sensitive", "Case-Sensitive Naming Policy", "Use case-sensitive forbidden name and token matching.", bool, related_check_ids=(USD_PRIM_NAMES_NO_FORBIDDEN_TOKENS, USD_FORBIDDEN_PRIM_NAMES)),
    ConfigFieldDefinition("hierarchy.require_single_root", "Require Single Root Prim", "Require exactly one prim below the pseudo-root.", bool, related_check_ids=(USD_SINGLE_ROOT_PRIM_REQUIRED,)),
    ConfigFieldDefinition("hierarchy.required_paths_csv", "Required Hierarchy Paths", "Comma-separated prim paths that must exist.", str, related_check_ids=(USD_REQUIRED_HIERARCHY_PATHS_EXIST,)),
    ConfigFieldDefinition("hierarchy.geometry_root_path", "Geometry Root Path", "Prim path below which mesh prims should be parented.", str, related_check_ids=(USD_MESHES_UNDER_REQUIRED_SCOPE,)),
    ConfigFieldDefinition("hierarchy.require_meshes_under_geometry_root", "Require Meshes Under Geometry Root", "Enable geometry-root hierarchy enforcement.", bool, related_check_ids=(USD_MESHES_UNDER_REQUIRED_SCOPE,)),
    ConfigFieldDefinition("transforms.require_identity_root", "Require Identity Root Transform", "Require the default root prim to have an identity local transform.", bool, related_check_ids=(USD_ROOT_TRANSFORM_IDENTITY,)),
    ConfigFieldDefinition("transforms.allow_negative_scale", "Allow Negative Scale", "Allow negative scale components.", bool, related_check_ids=(USD_NEGATIVE_SCALE_ALLOWED,)),
    ConfigFieldDefinition("transforms.allow_matrix_ops", "Allow Matrix Xform Ops", "Allow xformOp:transform matrix operations.", bool, related_check_ids=(USD_MATRIX_XFORM_OPS_ALLOWED,)),
    ConfigFieldDefinition("transforms.maximum_xform_ops", "Maximum Xform Ops", "Maximum ordered transform operations per prim.", int, 0, 128, related_check_ids=(USD_XFORM_OP_COUNT_LIMIT,)),
    ConfigFieldDefinition("transforms.zero_scale_tolerance", "Zero Scale Tolerance", "Absolute scale value treated as zero.", float, 0.0, 1.0, related_check_ids=(USD_TRANSFORM_SCALE_NONZERO,)),
    ConfigFieldDefinition("variants.required_sets_csv", "Required Variant Sets", "Comma-separated variant-set names required somewhere in the stage.", str, related_check_ids=(USD_REQUIRED_VARIANT_SETS_EXIST,)),
    ConfigFieldDefinition("variants.require_authored_selections", "Require Authored Variant Selections", "Require every variant set to have a selected option.", bool, related_check_ids=(USD_VARIANT_SELECTIONS_AUTHORED,)),
    ConfigFieldDefinition("variants.maximum_sets_per_prim", "Maximum Variant Sets Per Prim", "Maximum number of variant sets on one prim.", int, 0, 128, related_check_ids=(USD_VARIANT_SET_COUNT_LIMIT,)),
    ConfigFieldDefinition("cameras.required", "Require Camera", "Require at least one camera prim.", bool, related_check_ids=(USD_CAMERA_REQUIRED,)),
    ConfigFieldDefinition("cameras.maximum_count", "Maximum Camera Count", "Maximum cameras allowed in the stage.", int, 0, 10000, related_check_ids=(USD_CAMERA_COUNT_LIMIT,)),
    ConfigFieldDefinition("cameras.render_camera_name", "Render Camera Name", "Required render-camera prim name.", str, related_check_ids=(USD_RENDER_CAMERA_EXISTS,)),
    ConfigFieldDefinition("cameras.require_render_camera", "Require Render Camera", "Require a camera matching the configured render-camera name.", bool, related_check_ids=(USD_RENDER_CAMERA_EXISTS,)),
    ConfigFieldDefinition("cameras.minimum_focal_length", "Minimum Focal Length", "Minimum accepted camera focal length.", float, 0.001, 100000.0, unit="mm", related_check_ids=(USD_CAMERA_FOCAL_LENGTH_VALID,)),
    ConfigFieldDefinition("cameras.maximum_focal_length", "Maximum Focal Length", "Maximum accepted camera focal length.", float, 0.001, 100000.0, unit="mm", related_check_ids=(USD_CAMERA_FOCAL_LENGTH_VALID,)),
    ConfigFieldDefinition("cameras.minimum_near_clip", "Minimum Near Clip", "Smallest accepted near clipping plane.", float, 0.000001, 1000000.0, related_check_ids=(USD_CAMERA_CLIPPING_RANGE_VALID,)),
    ConfigFieldDefinition("cameras.maximum_far_clip", "Maximum Far Clip", "Largest accepted far clipping plane.", float, 0.001, 1000000000.0, related_check_ids=(USD_CAMERA_CLIPPING_RANGE_VALID,)),
    ConfigFieldDefinition("cameras.allow_animation", "Allow Camera Animation", "Allow time-varying camera attributes.", bool, related_check_ids=(USD_CAMERA_ANIMATION_ALLOWED,)),
    ConfigFieldDefinition("instancing.maximum_instances", "Maximum Native Instances", "Maximum native USD instances.", int, 0, 100000000, related_check_ids=(USD_INSTANCE_COUNT_LIMIT,)),
    ConfigFieldDefinition("instancing.maximum_point_instances", "Maximum Point Instances", "Maximum total PointInstancer instances.", int, 0, 100000000, related_check_ids=(USD_POINT_INSTANCE_COUNT_LIMIT,)),
    ConfigFieldDefinition("instancing.require_valid_prototypes", "Require Valid Instance Prototypes", "Require native and point instances to have valid prototypes.", bool, related_check_ids=(USD_POINT_INSTANCER_PROTOTYPES_VALID,)),
    ConfigFieldDefinition("packaging.allow_parent_directory_escape", "Allow Parent Directory Escape", "Allow dependency paths containing '..'.", bool, related_check_ids=(USD_NO_PARENT_DIRECTORY_ESCAPES,)),
    ConfigFieldDefinition("packaging.allow_absolute_dependency_paths", "Allow Absolute Dependency Paths", "Allow absolute reference and payload paths.", bool, related_check_ids=(USD_NO_ABSOLUTE_DEPENDENCY_PATHS,)),
    ConfigFieldDefinition("packaging.allow_temporary_dependencies", "Allow Temporary Dependencies", "Allow temp, preview, copy, or backup dependency paths.", bool, related_check_ids=(USD_NO_TEMPORARY_DEPENDENCIES,)),
    ConfigFieldDefinition("packaging.maximum_dependency_count", "Maximum Dependency Count", "Maximum references and payloads in the stage.", int, 0, 10000000, related_check_ids=(USD_DEPENDENCY_COUNT_LIMIT,)),
    ConfigFieldDefinition("packaging.allowed_extensions_csv", "Allowed Source Extensions", "Comma-separated allowed source extensions.", str, related_check_ids=(USD_SOURCE_EXTENSION_ALLOWED,)),
    ConfigFieldDefinition("packaging.filename_pattern", "Source Filename Pattern", "Regular expression required for the source filename.", str, related_check_ids=(USD_SOURCE_FILENAME_VALID,)),
)

FIELDS = FIELDS + ADDITIONAL_FIELDS
CONFIG_FIELDS = {field.path: field for field in FIELDS}
