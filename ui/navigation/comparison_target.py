from dataclasses import dataclass


@dataclass(frozen=True)
class ComparisonTarget:
    source_path: str
    side: str
    kind: str = "stage"
    prim_path: str = ""
    property_path: str = ""


def resolve_comparison_target(comparison, change, side="auto"):
    side = _resolve_side(change, side)
    source_path = comparison.previous_source if side == "previous" else comparison.current_source
    property_path = _usd_property_path(change.property_path)
    path = property_path or _usd_path(change.path)

    if property_path:
        return ComparisonTarget(source_path, side, "property", _owning_prim(property_path), property_path)
    if _is_property_path(path):
        return ComparisonTarget(source_path, side, "property", _owning_prim(path), path)
    if _is_prim_path(path):
        return ComparisonTarget(source_path, side, "prim", path)
    return ComparisonTarget(source_path, side)


def _resolve_side(change, side):
    if side in {"previous", "current"}:
        return side
    hint = str(change.source_hint or "").lower()
    if hint in {"previous", "current"}:
        return hint
    return "previous" if change.kind.value == "REMOVED" else "current"


def _usd_property_path(value):
    path = _usd_path(value)
    return path if _is_property_path(path) else ""


def _usd_path(value):
    text = str(value or "").strip()
    if not text.startswith("/") or text == "/" or any(char.isspace() for char in text):
        return ""
    return text


def _is_property_path(path):
    return bool(path and "." in path.rsplit("/", 1)[-1])


def _is_prim_path(path):
    return bool(path and not _is_property_path(path))


def _owning_prim(path):
    return path.rsplit(".", 1)[0]
