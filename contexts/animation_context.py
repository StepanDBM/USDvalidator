from dataclasses import dataclass, field


@dataclass
class AnimationStatistics:
    invalid_time_samples: list[dict] = field(default_factory=list)
    time_sample_count: int = 0
