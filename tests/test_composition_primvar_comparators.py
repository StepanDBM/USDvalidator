from comparison.composition_comparators import (
    CollectionComparator,
    CompositionArcComparator,
    GeomSubsetComparator,
    PrimvarComparator,
    RelationshipComparator,
    SublayerComparator,
)
from comparison.models import (
    ChangeImpact,
    ChangeKind,
    CollectionSnapshot,
    CompositionArcSnapshot,
    GeomSubsetSnapshot,
    PathArcSnapshot,
    PrimvarSnapshot,
    RelationshipSnapshot,
    StageComparisonSnapshot,
    SublayerSnapshot,
)


def _snapshot(**values):
    defaults = {
        "source_path": "test.usda",
        "metadata": {},
        "prims": {},
        "meshes": {},
        "dependencies": (),
        "animation": {},
    }
    defaults.update(values)
    return StageComparisonSnapshot(**defaults)


def test_sublayer_order_and_offsets_are_compared():
    previous = _snapshot(sublayers=(
        SublayerSnapshot("root", 0, "a.usda", 0.0, 1.0),
        SublayerSnapshot("root", 1, "b.usda", 0.0, 1.0),
    ))
    current = _snapshot(sublayers=(
        SublayerSnapshot("root", 0, "b.usda", 10.0, 2.0),
        SublayerSnapshot("root", 1, "a.usda", 0.0, 1.0),
    ))
    changes = SublayerComparator().compare(previous, current)
    changed = {item.property_path for item in changes if item.kind is ChangeKind.CHANGED}
    assert {"sublayers", "sublayer_offsets"} <= changed


def test_dependency_paths_are_paired_and_transitions_are_explicit():
    old = CompositionArcSnapshot("/World", "reference", "old.usda", "/Asset", "prepended", False, True)
    new = CompositionArcSnapshot("/World", "reference", "C:/publish/new.usda", "/Model", "prepended", True, True)
    previous = _snapshot(composition_arcs={(old.prim_path, old.arc_type, "old"): old})
    current = _snapshot(composition_arcs={(new.prim_path, new.arc_type, "new"): new})
    changes = CompositionArcComparator().compare(previous, current)
    changed = {item.property_path for item in changes if item.kind is ChangeKind.CHANGED}
    assert {"asset_path", "target_prim_path", "absolute"} <= changed


def test_inherits_and_specializes_are_compared():
    arc = PathArcSnapshot("/World/Model", "inherit", "/_class_Model")
    changes = CompositionArcComparator().compare(
        _snapshot(),
        _snapshot(path_arcs={(arc.prim_path, arc.arc_type, arc.target_path): arc}),
    )
    assert any(item.kind is ChangeKind.ADDED and item.property_path == "inherit" for item in changes)


def test_relationships_and_collections_are_compared():
    relationship_old = RelationshipSnapshot("/World.link", ("/A",), ("/A",))
    relationship_new = RelationshipSnapshot("/World.link", ("/B",), ("/B",))
    changes = RelationshipComparator().compare(
        _snapshot(relationships={relationship_old.property_path: relationship_old}),
        _snapshot(relationships={relationship_new.property_path: relationship_new}),
    )
    assert any(item.property_path == "targets" and item.kind is ChangeKind.CHANGED for item in changes)

    collection_old = CollectionSnapshot("/World", "render", ("/A",), (), "expandPrims", False)
    collection_new = CollectionSnapshot("/World", "render", ("/B",), ("/C",), "explicitOnly", True)
    changes = CollectionComparator().compare(
        _snapshot(collections={(collection_old.prim_path, collection_old.name): collection_old}),
        _snapshot(collections={(collection_new.prim_path, collection_new.name): collection_new}),
    )
    assert {"includes", "excludes", "expansion_rule", "include_root"} <= {
        item.property_path for item in changes if item.kind is ChangeKind.CHANGED
    }


def test_geom_subset_membership_and_material_are_compared():
    old = GeomSubsetSnapshot("/M/faces", "materialBind", "partition", "face", 3, "old", "/Looks/A")
    new = GeomSubsetSnapshot("/M/faces", "materialBind", "partition", "face", 3, "new", "/Looks/B")
    changes = GeomSubsetComparator().compare(
        _snapshot(geom_subsets={old.path: old}),
        _snapshot(geom_subsets={new.path: new}),
    )
    changed = {item.property_path for item in changes if item.kind is ChangeKind.CHANGED}
    assert {"indices_hash", "material_path"} <= changed


def test_general_and_uv_primvar_contracts_are_compared():
    old = PrimvarSnapshot("/M.primvars:st", "texCoord2f[]", "TexCoord", "vertex", 1, False, 4, 0, "a", "", True)
    new = PrimvarSnapshot("/M.primvars:st", "texCoord2f[]", "TexCoord", "faceVarying", 1, True, 6, 6, "b", "i", True)
    changes = PrimvarComparator().compare(
        _snapshot(primvars={old.property_path: old}),
        _snapshot(primvars={new.property_path: new}),
    )
    changed = {item.property_path for item in changes if item.kind is ChangeKind.CHANGED}
    assert {"interpolation", "indexed", "values_hash", "indices_hash"} <= changed
    assert next(item for item in changes if item.property_path == "interpolation").impact is ChangeImpact.HIGH
