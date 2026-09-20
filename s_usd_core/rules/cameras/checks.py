from s_usd_core.rules.common import result
from s_usd_core.validation.check_ids import (
    USD_CAMERA_ANIMATION_ALLOWED,
    USD_CAMERA_CLIPPING_RANGE_VALID,
    USD_CAMERA_COUNT_LIMIT,
    USD_CAMERA_FOCAL_LENGTH_VALID,
    USD_CAMERA_REQUIRED,
    USD_RENDER_CAMERA_EXISTS,
)


def check_camera_required(context, runtime_context):
    required = runtime_context.config.cameras.required
    count = len(context.pipeline.cameras)
    return result(USD_CAMERA_REQUIRED, "Camera Required", "Cameras", runtime_context, not required or count > 0, f"Camera count: {count}; required: {required}.", details={"count": count, "required": required}, suggestion="Author at least one camera.")


def check_camera_count_limit(context, runtime_context):
    count = len(context.pipeline.cameras)
    limit = runtime_context.config.cameras.maximum_count
    return result(USD_CAMERA_COUNT_LIMIT, "Camera Count Limit", "Cameras", runtime_context, count <= limit, f"Camera count {count}; allowed maximum {limit}.", details={"count": count, "limit": limit}, suggestion="Remove unnecessary cameras or override the limit.")


def check_render_camera_exists(context, runtime_context):
    config = runtime_context.config.cameras
    paths = [item.path for item in context.pipeline.cameras if item.path.rsplit("/", 1)[-1] == config.render_camera_name]
    passed = not config.require_render_camera or bool(paths)
    return result(USD_RENDER_CAMERA_EXISTS, "Render Camera Exists", "Cameras", runtime_context, passed, f"Render camera {config.render_camera_name!r} found: {bool(paths)}.", details={"paths": paths, "required": config.require_render_camera}, suggestion="Author the configured render camera.")


def check_camera_focal_length_valid(context, runtime_context):
    config = runtime_context.config.cameras
    invalid = [item.path for item in context.pipeline.cameras if not config.minimum_focal_length <= item.focal_length <= config.maximum_focal_length]
    return result(USD_CAMERA_FOCAL_LENGTH_VALID, "Camera Focal Length Valid", "Cameras", runtime_context, not invalid, f"Cameras outside the focal-length range: {len(invalid)}.", details={"paths": invalid, "minimum": config.minimum_focal_length, "maximum": config.maximum_focal_length}, suggestion="Use a profile-approved focal length.")


def check_camera_clipping_range_valid(context, runtime_context):
    config = runtime_context.config.cameras
    invalid = [item.path for item in context.pipeline.cameras if item.clipping_range[0] < config.minimum_near_clip or item.clipping_range[1] > config.maximum_far_clip or item.clipping_range[0] >= item.clipping_range[1]]
    return result(USD_CAMERA_CLIPPING_RANGE_VALID, "Camera Clipping Range Valid", "Cameras", runtime_context, not invalid, f"Cameras with invalid clipping ranges: {len(invalid)}.", details={"paths": invalid, "minimum_near": config.minimum_near_clip, "maximum_far": config.maximum_far_clip}, suggestion="Correct camera near and far clipping values.")


def check_camera_animation_allowed(context, runtime_context):
    allowed = runtime_context.config.cameras.allow_animation
    invalid = [item.path for item in context.pipeline.cameras if not allowed and item.time_varying]
    return result(USD_CAMERA_ANIMATION_ALLOWED, "Camera Animation Allowed", "Cameras", runtime_context, not invalid, f"Animated cameras forbidden by profile: {len(invalid)}.", details={"paths": invalid, "allowed": allowed}, suggestion="Remove camera animation or allow it in the profile.")
