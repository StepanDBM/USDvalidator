from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AttributeOverride:
    path: str
    value: Any
    enabled: bool = True

    def __post_init__(self):
        if not self.path.strip():
            raise ValueError("Override path cannot be empty.")

    @classmethod
    def from_dict(cls, data):
        return cls(
            path=data["path"],
            value=data.get("value"),
            enabled=data.get("enabled", True),
        )

    def to_dict(self):
        return {
            "path": self.path,
            "value": self.value,
            "enabled": self.enabled,
        }