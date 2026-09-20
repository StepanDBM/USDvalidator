from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PropertyRow:
    kind: str
    name: str
    value: str
    raw_value: object = None


@dataclass(frozen=True)
class StageStatistics:
    prims: int = 0
    meshes: int = 0
    points: int = 0
    materials: int = 0
    shaders: int = 0
    cameras: int = 0
    lights: int = 0
