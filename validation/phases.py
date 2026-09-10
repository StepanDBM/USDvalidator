# validation/phases.py

EXECUTION_PHASES = (
    "open",
    "metadata",
    "structure",
    "composition",
    "dependencies",
    "geometry",
    "shading",
    "animation",
    "performance",
    "publish"
)

_PHASE_ORDER = {phase: index for index, phase in enumerate(EXECUTION_PHASES)}


def phase_order(phase):
    if phase not in _PHASE_ORDER:
        raise ValueError(f"Unknown validation phase: {phase}")
    return _PHASE_ORDER[phase]
