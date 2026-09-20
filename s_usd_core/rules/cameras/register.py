from s_usd_core.contexts import StageHealthContext
from s_usd_core.validation.check_ids import (
    USD_CAMERA_REQUIRED,
    USD_CAMERA_COUNT_LIMIT,
    USD_RENDER_CAMERA_EXISTS,
    USD_CAMERA_FOCAL_LENGTH_VALID,
    USD_CAMERA_CLIPPING_RANGE_VALID,
    USD_CAMERA_ANIMATION_ALLOWED,
)
from s_usd_core.validation.enums import Severity
from s_usd_core.validation.models import CheckDefinition

from .checks import (
    check_camera_required,
    check_camera_count_limit,
    check_render_camera_exists,
    check_camera_focal_length_valid,
    check_camera_clipping_range_valid,
    check_camera_animation_allowed,
)


def register_cameras_checks(registry):
    entries = (
        (USD_CAMERA_REQUIRED, "Camera Required", check_camera_required, Severity.ERROR),
        (USD_CAMERA_COUNT_LIMIT, "Camera Count Limit", check_camera_count_limit, Severity.WARNING),
        (USD_RENDER_CAMERA_EXISTS, "Render Camera Exists", check_render_camera_exists, Severity.ERROR),
        (USD_CAMERA_FOCAL_LENGTH_VALID, "Camera Focal Length Valid", check_camera_focal_length_valid, Severity.WARNING),
        (USD_CAMERA_CLIPPING_RANGE_VALID, "Camera Clipping Range Valid", check_camera_clipping_range_valid, Severity.ERROR),
        (USD_CAMERA_ANIMATION_ALLOWED, "Camera Animation Allowed", check_camera_animation_allowed, Severity.WARNING),
    )

    for check_id, label, func, severity in entries:
        registry.register(CheckDefinition(
            check_id=check_id,
            label=label,
            description=label,
            func=func,
            target_type=StageHealthContext,
            category="Cameras",
            phase="structure",
            default_severity=severity,
            tags=("cameras", "publish"),
        ))
