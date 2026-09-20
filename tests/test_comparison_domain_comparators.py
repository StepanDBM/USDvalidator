from s_usd_core.comparison.lookdev_comparators import (
    MaterialBindingComparator,
    MaterialComparator,
    ShaderComparator,
)
from s_usd_core.comparison.models import (
    ChangeImpact,
    ChangeKind,
    MaterialBindingSnapshot,
    MaterialSnapshot,
    ShaderSnapshot,
    StageComparisonSnapshot,
    VariantSnapshot,
)
from s_usd_core.comparison.variant_comparator import VariantComparator


def _snapshot(**domains):
    values = {
        "source_path": "test.usda",
        "metadata": {},
        "prims": {},
        "meshes": {},
        "dependencies": (),
        "animation": {},
    }
    values.update(domains)
    return StageComparisonSnapshot(**values)


def test_variant_selection_change_is_high_impact():
    old = VariantSnapshot("/World", "lod", ("low", "high"), "low")
    new = VariantSnapshot("/World", "lod", ("low", "high"), "high")
    previous = _snapshot(variants={(old.prim_path, old.name): old})
    current = _snapshot(variants={(new.prim_path, new.name): new})
    changes = VariantComparator().compare(previous, current)
    change = next(item for item in changes if item.property_path == "selection")
    assert change.kind is ChangeKind.CHANGED
    assert change.impact is ChangeImpact.HIGH
    assert "USD_VARIANT_SELECTIONS_VALID" in change.related_check_ids


def test_material_surface_disconnection_is_high_impact():
    old = MaterialSnapshot("/Looks/Body", True, False, False, 1)
    new = MaterialSnapshot("/Looks/Body", False, False, False, 1)
    changes = MaterialComparator().compare(
        _snapshot(materials={old.path: old}),
        _snapshot(materials={new.path: new}),
    )
    change = next(item for item in changes if item.property_path == "surface_connected")
    assert change.impact is ChangeImpact.HIGH


def test_shader_id_and_asset_changes_are_detected():
    old = ShaderSnapshot("/Looks/Body/Shader", "UsdPreviewSurface", "id", 2, 1, 1, ("old.png",))
    new = ShaderSnapshot("/Looks/Body/Shader", "CustomSurface", "id", 2, 1, 1, ("new.png",))
    changes = ShaderComparator().compare(
        _snapshot(shaders={old.path: old}),
        _snapshot(shaders={new.path: new}),
    )
    changed = {item.property_path for item in changes if item.kind is ChangeKind.CHANGED}
    assert {"shader_id", "asset_inputs"} <= changed


def test_unresolved_material_binding_is_critical():
    old = MaterialBindingSnapshot("/World/Body", "/Looks/Body", True, True)
    new = MaterialBindingSnapshot("/World/Body", "/Looks/Body", True, False)
    changes = MaterialBindingComparator().compare(
        _snapshot(material_bindings={old.prim_path: old}),
        _snapshot(material_bindings={new.prim_path: new}),
    )
    change = next(item for item in changes if item.property_path == "resolved")
    assert change.impact is ChangeImpact.CRITICAL
    assert "USD_MATERIAL_BINDINGS_RESOLVE" in change.related_check_ids
