import hashlib
import json
import os

from pxr import Sdf, Usd, UsdGeom, UsdShade

from .models import (
    CollectionSnapshot,
    CompositionArcSnapshot,
    GeomSubsetSnapshot,
    PathArcSnapshot,
    PrimvarSnapshot,
    RelationshipSnapshot,
    SublayerSnapshot,
)


def extract_extended_domains(stage):
    return {
        "sublayers": _sublayers(stage),
        "composition_arcs": _composition_arcs(stage),
        "path_arcs": _path_arcs(stage),
        "relationships": _relationships(stage),
        "collections": _collections(stage),
        "geom_subsets": _geom_subsets(stage),
        "primvars": _primvars(stage),
    }


def _sublayers(stage):
    result = []
    session = stage.GetSessionLayer()
    for layer in stage.GetUsedLayers():
        if layer == session:
            continue
        for index, path in enumerate(layer.subLayerPaths):
            offset = layer.subLayerOffsets[index]
            result.append(SublayerSnapshot(
                layer.identifier,
                index,
                path,
                float(offset.offset),
                float(offset.scale),
            ))
    return tuple(sorted(result, key=lambda item: (item.layer_identifier, item.index)))


def _composition_arcs(stage):
    result = {}
    root = stage.GetRootLayer()
    for prim in stage.TraverseAll():
        for arc_type, metadata in (("reference", "references"), ("payload", "payload")):
            value = prim.GetMetadata(metadata)
            if not value:
                continue
            entries = (
                ("explicit", value.explicitItems),
                ("prepended", value.prependedItems),
                ("appended", value.appendedItems),
                ("added", value.addedItems),
            )
            for position, items in entries:
                for item in items:
                    asset_path = item.assetPath
                    target = str(item.primPath)
                    key = (prim.GetPath().pathString, arc_type, f"{asset_path}:{target}")
                    resolved = bool(Sdf.ComputeAssetPathRelativeToLayer(root, asset_path)) if asset_path else True
                    result[key] = CompositionArcSnapshot(
                        prim.GetPath().pathString,
                        arc_type,
                        asset_path,
                        target,
                        position,
                        os.path.isabs(asset_path),
                        resolved,
                    )
    return result


def _path_arcs(stage):
    result = {}
    for prim in stage.TraverseAll():
        for arc_type, metadata in (("inherit", "inheritPaths"), ("specialize", "specializes")):
            value = prim.GetMetadata(metadata)
            if not value:
                continue
            paths = set(value.GetAddedOrExplicitItems())
            paths.update(value.prependedItems)
            paths.update(value.appendedItems)
            for target in paths:
                snapshot = PathArcSnapshot(prim.GetPath().pathString, arc_type, str(target))
                result[(snapshot.prim_path, arc_type, snapshot.target_path)] = snapshot
    return result


def _relationships(stage):
    result = {}
    for prim in stage.TraverseAll():
        for relationship in prim.GetRelationships():
            path = relationship.GetPath().pathString
            targets = tuple(target.pathString for target in relationship.GetTargets())
            forwarded = tuple(target.pathString for target in relationship.GetForwardedTargets())
            result[path] = RelationshipSnapshot(path, targets, forwarded)
    return result


def _collections(stage):
    result = {}
    for prim in stage.TraverseAll():
        names = set()
        for prop in prim.GetProperties():
            name = prop.GetName()
            if name.startswith("collection:"):
                parts = name.split(":")
                if len(parts) >= 3:
                    names.add(parts[1])
        for name in names:
            api = Usd.CollectionAPI(prim, name)
            includes = tuple(path.pathString for path in api.GetIncludesRel().GetTargets())
            excludes = tuple(path.pathString for path in api.GetExcludesRel().GetTargets())
            snapshot = CollectionSnapshot(
                prim.GetPath().pathString,
                name,
                includes,
                excludes,
                api.GetExpansionRuleAttr().Get() or "expandPrims",
                bool(api.GetIncludeRootAttr().Get()),
            )
            result[(snapshot.prim_path, name)] = snapshot
    return result


def _geom_subsets(stage):
    result = {}
    for prim in stage.TraverseAll():
        if not prim.IsA(UsdGeom.Subset):
            continue
        subset = UsdGeom.Subset(prim)
        indices = tuple(subset.GetIndicesAttr().Get() or ())
        binding = UsdShade.MaterialBindingAPI(prim)
        material, _ = binding.ComputeBoundMaterial()
        family_name = subset.GetFamilyNameAttr().Get() or ""
        parent = prim.GetParent()
        family_type = UsdGeom.Subset.GetFamilyType(UsdGeom.Imageable(parent), family_name) if family_name else ""
        snapshot = GeomSubsetSnapshot(
            prim.GetPath().pathString,
            family_name,
            str(family_type),
            subset.GetElementTypeAttr().Get() or "face",
            len(indices),
            _hash(indices),
            material.GetPath().pathString if material else "",
        )
        result[snapshot.path] = snapshot
    return result


def _primvars(stage):
    result = {}
    for prim in stage.TraverseAll():
        for primvar in UsdGeom.PrimvarsAPI(prim).GetPrimvars():
            value = primvar.Get()
            indices = primvar.GetIndices() if primvar.IsIndexed() else ()
            property_path = primvar.GetAttr().GetPath().pathString
            type_name = str(primvar.GetTypeName())
            role = str(primvar.GetTypeName().role)
            name = primvar.GetPrimvarName()
            snapshot = PrimvarSnapshot(
                property_path,
                type_name,
                role,
                primvar.GetInterpolation() or "",
                int(primvar.GetElementSize()),
                bool(primvar.IsIndexed()),
                _count(value),
                _count(indices),
                _hash(value),
                _hash(indices),
                name in {"st", "uv", "map1"} or "TexCoord" in type_name,
            )
            result[property_path] = snapshot
    return result


def _count(value):
    try:
        return len(value)
    except TypeError:
        return int(value is not None)


def _hash(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
