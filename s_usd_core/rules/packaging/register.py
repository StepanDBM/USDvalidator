from s_usd_core.contexts import StageHealthContext
from s_usd_core.validation.check_ids import (
    USD_NO_PARENT_DIRECTORY_ESCAPES,
    USD_NO_ABSOLUTE_DEPENDENCY_PATHS,
    USD_NO_TEMPORARY_DEPENDENCIES,
    USD_DEPENDENCY_COUNT_LIMIT,
    USD_SOURCE_EXTENSION_ALLOWED,
    USD_SOURCE_FILENAME_VALID,
)
from s_usd_core.validation.enums import Severity
from s_usd_core.validation.models import CheckDefinition

from .checks import (
    check_no_parent_directory_escapes,
    check_no_absolute_dependency_paths,
    check_no_temporary_dependencies,
    check_dependency_count_limit,
    check_source_extension_allowed,
    check_source_filename_valid,
)


def register_packaging_checks(registry):
    entries = (
        (USD_NO_PARENT_DIRECTORY_ESCAPES, "No Parent Directory Escapes", check_no_parent_directory_escapes, Severity.ERROR),
        (USD_NO_ABSOLUTE_DEPENDENCY_PATHS, "No Absolute Dependency Paths", check_no_absolute_dependency_paths, Severity.ERROR),
        (USD_NO_TEMPORARY_DEPENDENCIES, "No Temporary Dependencies", check_no_temporary_dependencies, Severity.WARNING),
        (USD_DEPENDENCY_COUNT_LIMIT, "Dependency Count Limit", check_dependency_count_limit, Severity.WARNING),
        (USD_SOURCE_EXTENSION_ALLOWED, "Source Extension Allowed", check_source_extension_allowed, Severity.ERROR),
        (USD_SOURCE_FILENAME_VALID, "Source Filename Valid", check_source_filename_valid, Severity.ERROR),
    )

    for check_id, label, func, severity in entries:
        registry.register(CheckDefinition(
            check_id=check_id,
            label=label,
            description=label,
            func=func,
            target_type=StageHealthContext,
            category="Packaging",
            phase="publish",
            default_severity=severity,
            tags=("packaging", "publish"),
        ))
