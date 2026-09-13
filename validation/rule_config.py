from dataclasses import dataclass, field


@dataclass
class GeometryRuleConfig:
    polygon_count_limit: int = 100000


@dataclass
class MetadataRuleConfig:
    allowed_up_axes: tuple[str, ...] = ("Y", "Z")
    minimum_meters_per_unit: float = 0.000001


@dataclass
class AnimationRuleConfig:
    allowed_frame_rates: tuple[float, ...] = (
        23.976,
        24.0,
        25.0,
        29.97,
        30.0,
        48.0,
        50.0,
        59.94,
        60.0,
    )


@dataclass
class ValidationRuleConfig:
    geometry: GeometryRuleConfig = field(default_factory=GeometryRuleConfig)
    metadata: MetadataRuleConfig = field(default_factory=MetadataRuleConfig)
    animation: AnimationRuleConfig = field(default_factory=AnimationRuleConfig)