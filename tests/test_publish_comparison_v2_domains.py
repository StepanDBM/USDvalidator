from types import SimpleNamespace

from comparison.engine import SemanticComparisonEngine
from comparison.lookdev_comparators import ShaderComparator
from comparison.models import (
    CameraSnapshot,
    ChangeImpact,
    ChangeKind,
    InstancingSnapshot,
    LayerSnapshot,
    ShaderSnapshot,
    StageComparisonSnapshot,
    SurfaceSnapshot,
)
from comparison.publish_domain_comparators import (
    CameraComparator,
    InstancingComparator,
    LayerComparator,
    SurfaceComparator,
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


def _snapshot_key(item):
    for attribute in ("path", "prim_path", "identifier"):
        value = getattr(item, attribute, "")
        if value:
            return value
    raise ValueError(f"Snapshot has no usable identity: {item!r}")


def _changed(comparator, collection, old, new, field):
    previous = _snapshot(**{collection: {_snapshot_key(old): old}})
    current = _snapshot(**{collection: {_snapshot_key(new): new}})
    return next(
        change
        for change in comparator.compare(previous, current)
        if change.property_path == field
    )


def test_shader_values_and_topology_are_compared():
    old = ShaderSnapshot("/S", "id", "id", 1, 1, 1, (), (("roughness", "0.2"),), (("color", "/T.rgb"),))
    new = ShaderSnapshot("/S", "id", "id", 1, 1, 1, (), (("roughness", "0.8"),), (("color", "/U.rgb"),))
    changes = ShaderComparator().compare(
        _snapshot(shaders={old.path: old}),
        _snapshot(shaders={new.path: new}),
    )
    changed = {change.property_path for change in changes if change.kind is ChangeKind.CHANGED}
    assert {"input_values", "connections"} <= changed


def test_surface_camera_layer_and_instancing_domains():
    surface_old = SurfaceSnapshot("/M", True, 3, "vertex", True, ("st",), (("st", 3),), (("st", "vertex"),), (("st", True),))
    surface_new = SurfaceSnapshot("/M", True, 3, "faceVarying", True, ("st",), (("st", 3),), (("st", "faceVarying"),), (("st", True),))
    assert _changed(SurfaceComparator(), "surfaces", surface_old, surface_new, "normals_interpolation").impact is ChangeImpact.HIGH

    camera_old = CameraSnapshot("/Camera", "perspective", 35.0, (0.1, 1000.0), False)
    camera_new = CameraSnapshot("/Camera", "orthographic", 35.0, (0.1, 1000.0), False)
    assert _changed(CameraComparator(), "cameras", camera_old, camera_new, "projection").impact is ChangeImpact.HIGH

    layer_old = LayerSnapshot("root.usda", False, False, 1, "", "World")
    layer_new = LayerSnapshot("root.usda", False, False, 2, "", "World")
    assert _changed(LayerComparator(), "layers", layer_old, layer_new, "sublayer_count").kind is ChangeKind.CHANGED

    instance_old = InstancingSnapshot("/I", False, True, "/P", True, 2, 10, 0)
    instance_new = InstancingSnapshot("/I", False, True, "/P", True, 2, 10, 2)
    assert _changed(InstancingComparator(), "instancing", instance_old, instance_new, "invalid_proto_indices").impact is ChangeImpact.CRITICAL


def test_semantic_validation_correlation_marks_regression_and_resolution():
    semantic = SimpleNamespace(
        related_check_ids=("CHECK_A", "CHECK_B"),
        details={},
        validation_consequence="",
    )
    from comparison.models import SemanticChange
    semantic = SemanticChange(
        "Shaders", "/S", "Shader changed", ChangeKind.CHANGED,
        related_check_ids=("CHECK_A", "CHECK_B"),
    )
    passed = SimpleNamespace(status=SimpleNamespace(value="PASSED"))
    failed = SimpleNamespace(status=SimpleNamespace(value="FAILED"))
    previous = SimpleNamespace(results=[SimpleNamespace(check_id="CHECK_A", **passed.__dict__), SimpleNamespace(check_id="CHECK_B", **failed.__dict__)])
    current = SimpleNamespace(results=[SimpleNamespace(check_id="CHECK_A", **failed.__dict__), SimpleNamespace(check_id="CHECK_B", **passed.__dict__)])
    result = SimpleNamespace(changes=[semantic])
    SemanticComparisonEngine._correlate_validation(result, previous, current)
    assert "CHECK_A regressed" in result.changes[0].validation_consequence
    assert "CHECK_B resolved" in result.changes[0].validation_consequence
    assert len(result.changes[0].details["validation_correlation"]) == 2
