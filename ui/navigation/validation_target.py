from dataclasses import dataclass
from pxr import Sdf

@dataclass(frozen=True)
class ValidationTarget:
    source_path: str
    prim_path: str = ""
    property_path: str = ""
    kind: str = "stage"

def resolve_validation_target(report, result):
    details = result.details or {}
    candidates = []
    for key in ("property_path", "prim_path", "paths", "invalid_meshes", "primvars", "variant_sets"):
        value = details.get(key)
        candidates.extend(value if isinstance(value, (list, tuple, set)) else [value] if value else [])
    candidates.append(result.location)
    for value in candidates:
        text = str(value or "").strip()
        if not text.startswith("/"):
            continue
        try:
            path = Sdf.Path(text)
        except Exception:
            continue
        if path.IsPropertyPath():
            return ValidationTarget(str(report.source_path), path.GetPrimPath().pathString, path.pathString, "property")
        if path.IsPrimPath() and path != Sdf.Path.absoluteRootPath:
            return ValidationTarget(str(report.source_path), path.pathString, "", "prim")
    return ValidationTarget(str(report.source_path))
