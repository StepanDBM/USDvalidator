import re

from s_usd_core.rules.common import csv_values, result
from s_usd_core.validation.check_ids import (
    USD_DEPENDENCY_COUNT_LIMIT,
    USD_NO_ABSOLUTE_DEPENDENCY_PATHS,
    USD_NO_PARENT_DIRECTORY_ESCAPES,
    USD_NO_TEMPORARY_DEPENDENCIES,
    USD_SOURCE_EXTENSION_ALLOWED,
    USD_SOURCE_FILENAME_VALID,
)


def check_no_parent_directory_escapes(context, runtime_context):
    allowed = runtime_context.config.packaging.allow_parent_directory_escape
    invalid = [item.asset_path for item in context.pipeline.dependencies if not allowed and item.parent_escape]
    return result(USD_NO_PARENT_DIRECTORY_ESCAPES, "No Parent Directory Escapes", "Packaging", runtime_context, not invalid, f"Dependencies containing '..': {len(invalid)}.", details={"paths": invalid, "allowed": allowed}, suggestion="Use project-relative paths that do not escape the publish root.")


def check_no_absolute_dependency_paths(context, runtime_context):
    allowed = runtime_context.config.packaging.allow_absolute_dependency_paths
    invalid = [item.asset_path for item in context.pipeline.dependencies if not allowed and item.absolute]
    return result(USD_NO_ABSOLUTE_DEPENDENCY_PATHS, "No Absolute Dependency Paths", "Packaging", runtime_context, not invalid, f"Absolute dependency paths: {len(invalid)}.", details={"paths": invalid, "allowed": allowed}, suggestion="Use portable relative asset paths.")


def check_no_temporary_dependencies(context, runtime_context):
    allowed = runtime_context.config.packaging.allow_temporary_dependencies
    invalid = [item.asset_path for item in context.pipeline.dependencies if not allowed and item.temporary]
    return result(USD_NO_TEMPORARY_DEPENDENCIES, "No Temporary Dependencies", "Packaging", runtime_context, not invalid, f"Temporary dependency paths: {len(invalid)}.", details={"paths": invalid, "allowed": allowed}, suggestion="Replace temporary, preview, copy, or backup dependencies.")


def check_dependency_count_limit(context, runtime_context):
    count = len(context.pipeline.dependencies)
    limit = runtime_context.config.packaging.maximum_dependency_count
    return result(USD_DEPENDENCY_COUNT_LIMIT, "Dependency Count Limit", "Packaging", runtime_context, count <= limit, f"Dependency count {count}; allowed maximum {limit}.", details={"count": count, "limit": limit}, suggestion="Reduce dependency count or override the limit.")


def check_source_extension_allowed(context, runtime_context):
    allowed = {value.lower() for value in csv_values(runtime_context.config.packaging.allowed_extensions_csv)}
    extension = context.file.extension.lower()
    return result(USD_SOURCE_EXTENSION_ALLOWED, "Source Extension Allowed", "Packaging", runtime_context, extension in allowed, f"Source extension {extension!r}; allowed {sorted(allowed)}.", details={"extension": extension, "allowed": sorted(allowed)}, suggestion="Publish using an allowed USD extension.")


def check_source_filename_valid(context, runtime_context):
    pattern = runtime_context.config.packaging.filename_pattern
    valid = re.fullmatch(pattern, context.file.filename) is not None
    return result(USD_SOURCE_FILENAME_VALID, "Source Filename Valid", "Packaging", runtime_context, valid, f"Source filename {context.file.filename!r}; pattern {pattern!r}.", details={"filename": context.file.filename, "pattern": pattern}, suggestion="Rename the source file to match the publish naming pattern.")
