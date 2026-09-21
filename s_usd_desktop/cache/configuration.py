import os
from dataclasses import dataclass
from pathlib import Path


def default_cache_root():
    local_app_data = os.environ.get("LOCALAPPDATA")

    if local_app_data:
        return Path(local_app_data) / "Styopa" / "S-USDv" / "cache"

    return Path.home() / ".cache" / "Styopa" / "S-USDv"


@dataclass(frozen=True, slots=True)
class CacheConfiguration:
    root: Path = None
    maximum_bytes: int = 50 * 1024**3
    verify_on_access: bool = True

    def __post_init__(self):
        root = Path(self.root) if self.root is not None else default_cache_root()

        if self.maximum_bytes <= 0:
            raise ValueError("maximum_bytes must be greater than zero")

        object.__setattr__(self, "root", root.expanduser().resolve())
