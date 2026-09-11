from dataclasses import dataclass, field


@dataclass(frozen=True)
class ValidationProfile:
    name: str
    description: str = ""
    enabled_check_ids: frozenset[str] = field(default_factory=frozenset)
    disabled_check_ids: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Profile name cannot be empty.")

        if self.enabled_check_ids & self.disabled_check_ids:
            raise ValueError(
                "A check cannot be both enabled and disabled."
            )

DEFAULT_PROFILE = "layout_publish"