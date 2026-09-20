# rules/metadata/register.py

from s_usd_core.contexts import StageHealthContext
from s_usd_core.validation.check_ids import *
from s_usd_core.validation.enums import Severity
from s_usd_core.validation.models import CheckDefinition
from .checks import *


def register_metadata_checks(registry):
    entries = (
        (USD_DEFAULT_PRIM_AUTHORED, "Default Prim Authored", check_default_prim_authored, Severity.ERROR, ("metadata", "defaultPrim", "required")),
        (USD_DEFAULT_PRIM_VALID, "Default Prim Valid", check_default_prim_valid, Severity.ERROR, ("metadata", "defaultPrim", "required")),
        (USD_UP_AXIS_VALID, "Up Axis Valid", check_up_axis_valid, Severity.ERROR, ("metadata", "axis")),
        (USD_METERS_PER_UNIT_AUTHORED, "Meters Per Unit Authored", check_meters_per_unit_authored, Severity.ERROR, ("metadata", "scale")),
        (USD_METERS_PER_UNIT_VALID, "Meters Per Unit Valid", check_meters_per_unit_valid, Severity.ERROR, ("metadata", "scale")),
        (USD_ROOT_PRIM_NAME_VALID, "Root Prim Name Valid", check_root_prim_name_valid, Severity.ERROR, ("metadata", "naming", "root")),
        (USD_ROOT_PRIM_TYPE_VALID, "Root Prim Type Valid", check_root_prim_type_valid, Severity.ERROR, ("metadata", "root", "schema")),
        (USD_TIME_CODES_VALID, "Time Codes Valid", check_time_codes_valid, Severity.ERROR, ("metadata", "animation", "timing")),
        (USD_FRAME_RATE_VALID, "Frame Rate Valid", check_frame_rate_valid, Severity.ERROR, ("metadata", "animation", "timing")),
    )
    for check_id, label, func, severity, tags in entries:
        registry.register(CheckDefinition(check_id=check_id, label=label, description=label, func=func, target_type=StageHealthContext, category="Metadata", phase="metadata", default_severity=severity, tags=tags))
