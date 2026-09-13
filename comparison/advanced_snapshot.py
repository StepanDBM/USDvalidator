import hashlib
import json

from pxr import Sdf

from .models import (
    BlendShapeSnapshot,
    LightSnapshot,
    RenderProductSnapshot,
    RenderSettingsSnapshot,
    RenderVarSnapshot,
    SkeletonSnapshot,
    SkinningSnapshot,
    TimeConfigurationSnapshot,
    ValueClipSnapshot,
)


def extract_advanced_domains(stage):
    result = {
        "lights": {},
        "render_settings": {},
        "render_products": {},
        "render_vars": {},
        "skeletons": {},
        "skinning": {},
        "blend_shapes": {},
        "value_clips": {},
        "time_configuration": TimeConfigurationSnapshot(
            float(stage.GetStartTimeCode()),
            float(stage.GetEndTimeCode()),
            float(stage.GetFramesPerSecond()),
            float(stage.GetTimeCodesPerSecond()),
        ),
    }
    for prim in stage.TraverseAll():
        path = prim.GetPath().pathString
        type_name = prim.GetTypeName()
        if type_name.endswith("Light") or type_name in {"DomeLight", "GeometryLight"}:
            result["lights"][path] = _light(prim)
        elif type_name == "RenderSettings":
            result["render_settings"][path] = _render_settings(stage, prim)
        elif type_name == "RenderProduct":
            result["render_products"][path] = _render_product(prim)
        elif type_name == "RenderVar":
            result["render_vars"][path] = _render_var(prim)
        elif type_name == "Skeleton":
            result["skeletons"][path] = _skeleton(prim)
        elif type_name == "BlendShape":
            result["blend_shapes"][path] = _blend_shape(stage, prim)
        skinning = _skinning(prim)
        if skinning:
            result["skinning"][path] = skinning
        result["value_clips"].update(_value_clips(prim))
    return result


def _light(prim):
    shaping = tuple(sorted(
        (attr.GetName(), _value(attr.Get()))
        for attr in prim.GetAttributes()
        if attr.GetName().startswith("shaping:")
    ))
    texture_assets = tuple(sorted(
        _asset_path(attr.Get())
        for attr in prim.GetAttributes()
        if isinstance(attr.Get(), Sdf.AssetPath)
    ))
    return LightSnapshot(
        prim.GetPath().pathString,
        prim.GetTypeName(),
        _attr(prim, "intensity"),
        _attr(prim, "exposure"),
        _attr(prim, "color"),
        _attr(prim, "colorTemperature"),
        _attr(prim, "enableColorTemperature"),
        _attr(prim, "normalize"),
        shaping,
        texture_assets,
        any(attr.ValueMightBeTimeVarying() for attr in prim.GetAttributes()),
        _relationship_targets(prim, "collection:lightLink:includes"),
        _relationship_targets(prim, "collection:shadowLink:includes"),
    )


def _render_settings(stage, prim):
    active = stage.GetMetadata("renderSettingsPrimPath") == prim.GetPath()
    return RenderSettingsSnapshot(
        prim.GetPath().pathString,
        active,
        _first_target(prim, "camera"),
        _relationship_targets(prim, "products"),
        _tuple_attr(prim, "includedPurposes"),
        _tuple_attr(prim, "materialBindingPurposes"),
        _namespaced_settings(prim),
    )


def _render_product(prim):
    return RenderProductSnapshot(
        prim.GetPath().pathString,
        _attr(prim, "productType"),
        _attr(prim, "productName"),
        _first_target(prim, "camera"),
        _relationship_targets(prim, "orderedVars"),
        _attr(prim, "resolution"),
        _attr(prim, "pixelAspectRatio"),
        _attr(prim, "dataWindowNDC"),
        _namespaced_settings(prim),
    )


def _render_var(prim):
    return RenderVarSnapshot(
        prim.GetPath().pathString,
        _attr(prim, "sourceName"),
        _attr(prim, "sourceType"),
        _attr(prim, "dataType"),
        _namespaced_settings(prim),
    )


def _skeleton(prim):
    joints = tuple(str(item) for item in (_raw_attr(prim, "joints") or ()))
    parents = []
    indices = {joint: index for index, joint in enumerate(joints)}
    for joint in joints:
        parent = joint.rsplit("/", 1)[0] if "/" in joint else ""
        parents.append(indices.get(parent, -1))
    return SkeletonSnapshot(
        prim.GetPath().pathString,
        joints,
        tuple(parents),
        _hash(_raw_attr(prim, "bindTransforms")),
        _hash(_raw_attr(prim, "restTransforms")),
        _first_target(prim, "skel:animationSource"),
    )


def _skinning(prim):
    skeleton = _first_target(prim, "skel:skeleton")
    indices = _raw_attr(prim, "primvars:skel:jointIndices")
    weights = _raw_attr(prim, "primvars:skel:jointWeights")
    if not skeleton and indices is None and weights is None:
        return None
    indices_attr = prim.GetAttribute("primvars:skel:jointIndices")
    return SkinningSnapshot(
        prim.GetPath().pathString,
        skeleton,
        _hash(_raw_attr(prim, "skel:geomBindTransform")),
        _hash(indices),
        _hash(weights),
        len(indices or ()),
        int(indices_attr.GetMetadata("elementSize") or 1) if indices_attr else 1,
    )


def _blend_shape(stage, prim):
    path = prim.GetPath().pathString
    bound = []
    for candidate in stage.TraverseAll():
        targets = _relationship_targets(candidate, "skel:blendShapeTargets")
        if path in targets:
            bound.append(candidate.GetPath().pathString)
    inbetweens = tuple(sorted(
        attr.GetName() for attr in prim.GetAttributes()
        if attr.GetName().startswith("inbetweens:")
    ))
    return BlendShapeSnapshot(
        path,
        _hash(_raw_attr(prim, "offsets")),
        _hash(_raw_attr(prim, "normalOffsets")),
        _hash(_raw_attr(prim, "pointIndices")),
        inbetweens,
        tuple(sorted(bound)),
    )


def _value_clips(prim):
    clips = prim.GetMetadata("clips") or {}
    result = {}
    for name, values in clips.items():
        asset_paths = tuple(_asset_path(item) for item in values.get("assetPaths", ()))
        snapshot = ValueClipSnapshot(
            prim.GetPath().pathString,
            str(name),
            asset_paths,
            str(values.get("primPath", "")),
            _asset_path(values.get("manifestAssetPath")),
            _hash(values.get("active")),
            _hash(values.get("times")),
            _asset_path(values.get("templateAssetPath")),
            _value(values.get("templateStartTime")),
            _value(values.get("templateEndTime")),
            _value(values.get("templateStride")),
        )
        result[(snapshot.prim_path, snapshot.clip_set)] = snapshot
    return result


def _namespaced_settings(prim):
    excluded = {"visibility", "purpose", "extent"}
    return tuple(sorted(
        (attr.GetName(), _value(attr.Get()))
        for attr in prim.GetAttributes()
        if ":" in attr.GetName() and attr.GetName() not in excluded
    ))


def _raw_attr(prim, name):
    attr = prim.GetAttribute(name)
    return attr.Get() if attr else None


def _attr(prim, name):
    return _value(_raw_attr(prim, name))


def _tuple_attr(prim, name):
    value = _raw_attr(prim, name) or ()
    return tuple(str(item) for item in value)


def _relationship_targets(prim, name):
    relationship = prim.GetRelationship(name)
    return tuple(path.pathString for path in relationship.GetTargets()) if relationship else ()


def _first_target(prim, name):
    targets = _relationship_targets(prim, name)
    return targets[0] if targets else ""


def _asset_path(value):
    if isinstance(value, Sdf.AssetPath):
        return value.path
    return str(value or "")


def _value(value):
    return json.dumps(value, sort_keys=True, default=str) if value is not None else ""


def _hash(value):
    return hashlib.sha256(_value(value).encode("utf-8")).hexdigest()
