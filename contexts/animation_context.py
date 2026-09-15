from dataclasses import dataclass, field


@dataclass(frozen=True)
class AnimatedPropertyInfo:
    property_path: str
    time_samples: tuple[float, ...]
    time_varying: bool = True


@dataclass(frozen=True)
class ValueClipInfo:
    prim_path: str
    clip_set: str
    asset_paths: tuple[str, ...]
    clip_prim_path: str
    manifest_asset_path: str
    active: tuple[tuple, ...]
    times: tuple[tuple, ...]
    template_asset_path: str


@dataclass
class AnimationStatistics:
    invalid_time_samples: list[dict] = field(default_factory=list)
    time_sample_count: int = 0
    properties: list[AnimatedPropertyInfo] = field(default_factory=list)
    value_clips: list[ValueClipInfo] = field(default_factory=list)
