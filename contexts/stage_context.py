# contexts/stage_context.py

from dataclasses import dataclass


@dataclass
class StageContext:
    source_path: str
    exists: bool = False
    opened: bool = False
    root_layer: str = ""
    error_message: str = ""