# rules/animation/__init__.py

from .checks import (
    check_animation_frame_rate_valid,
    check_animation_has_no_invalid_time_samples,
    check_stage_frame_range_valid,
)
from .register import register_animation_checks

__all__ = [
    "check_animation_frame_rate_valid",
    "check_animation_has_no_invalid_time_samples",
    "check_stage_frame_range_valid",
    "register_animation_checks",
]