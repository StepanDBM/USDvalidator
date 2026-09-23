from enum import StrEnum


class VersionStatus(StrEnum):
    DRAFT = "draft"
    UPLOADED = "uploaded"
    VALIDATION_FAILED = "validation_failed"
    VALIDATED = "validated"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


TERMINAL_VERSION_STATUSES = frozenset({
    VersionStatus.PUBLISHED,
    VersionStatus.DEPRECATED
})
