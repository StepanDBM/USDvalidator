from enum import StrEnum


class ProjectStatus(StrEnum):
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    ARCHIVED = "archived"


PROJECT_STATUSES = tuple(item.value for item in ProjectStatus)
