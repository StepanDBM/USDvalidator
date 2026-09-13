from dataclasses import dataclass

from .check_ids import USD_MESH_POLYGON_COUNT_LIMIT


@dataclass(frozen=True)
class ConfigFieldDefinition:
    path: str
    label: str
    description: str
    value_type: type
    minimum: int | float | None = None
    maximum: int | float | None = None
    related_check_ids: tuple[str, ...] = ()


POLYGON_COUNT_LIMIT = ConfigFieldDefinition(
    path="geometry.polygon_count_limit",
    label="Polygon Count Limit",
    description="Maximum polygon count allowed for an individual USD mesh.",
    value_type=int,
    minimum=1,
    maximum=2147483647,
    related_check_ids=(USD_MESH_POLYGON_COUNT_LIMIT,),
)


CONFIG_FIELDS = {
    POLYGON_COUNT_LIMIT.path: POLYGON_COUNT_LIMIT,
}


def get_config_field(path):
    return CONFIG_FIELDS[path]


def get_config_fields():
    return tuple(CONFIG_FIELDS.values())


def get_fields_for_check(check_id):
    return tuple(
        field
        for field in CONFIG_FIELDS.values()
        if check_id in field.related_check_ids
    )