from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ViewportState:
    source_path: str = ""
    selected_path: str = ""
    error_message: str = ""
    stage_loaded: bool = False
