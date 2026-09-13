from types import SimpleNamespace

from comparison.advanced_comparators import (
    LightComparator,
    SkeletonComparator,
    TimeConfigurationComparator,
    ValueClipComparator,
)
from comparison.engine import SemanticComparisonEngine
from comparison.models import (
    ChangeImpact,
    ChangeKind,
    LightSnapshot,
    SemanticChange,
    SkeletonSnapshot,
    StageComparisonSnapshot,
    TimeConfigurationSnapshot,
    ValueClipSnapshot,
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


def test_light_linking_and_lux_facts_are_compared():
    old = LightSnapshot("/L", "SphereLight", "1", "0", "white", "6500", "false", "false", (), (), False, ("/A",), ())
    new = LightSnapshot("/L", "DomeLight", "2", "1", "blue", "4500", "true", "true", (), ("env.exr",), True, ("/B",), ("/C",))
    changes = LightComparator().compare(
        _snapshot(lights={old.path: old}),
        _snapshot(lights={new.path: new}),
    )
    changed = {change.property_path for change in changes if change.kind is ChangeKind.CHANGED}
    assert {"type_name", "intensity", "linked_paths", "shadow_linked_paths"} <= changed


def test_skeleton_topology_is_critical():
    old = SkeletonSnapshot("/Skel", ("root", "root/hip"), (-1, 0), "a", "r", "/Anim")
    new = SkeletonSnapshot("/Skel", ("root", "root/spine"), (-1, 0), "b", "r", "/Anim")
    changes = SkeletonComparator().compare(
        _snapshot(skeletons={old.path: old}),
        _snapshot(skeletons={new.path: new}),
    )
    topology = next(change for change in changes if change.property_path == "joints")
    assert topology.kind is ChangeKind.CHANGED
    assert topology.impact is ChangeImpact.CRITICAL


def test_value_clips_and_time_configuration_are_compared():
    old = ValueClipSnapshot("/Model", "default", ("a.usd",), "/Model", "manifest.usd", "a", "t", "", "", "", "")
    new = ValueClipSnapshot("/Model", "default", ("b.usd",), "/Asset", "manifest.usd", "b", "u", "", "", "", "")
    changes = ValueClipComparator().compare(
        _snapshot(value_clips={(old.prim_path, old.clip_set): old}),
        _snapshot(value_clips={(new.prim_path, new.clip_set): new}),
    )
    assert {"asset_paths", "clip_prim_path", "active_hash", "times_hash"} <= {
        change.property_path for change in changes if change.kind is ChangeKind.CHANGED
    }

    previous = _snapshot(time_configuration=TimeConfigurationSnapshot(1, 100, 24, 24))
    current = _snapshot(time_configuration=TimeConfigurationSnapshot(1, 120, 30, 30))
    changes = TimeConfigurationComparator().compare(previous, current)
    assert next(change for change in changes if change.property_path == "frames_per_second").impact is ChangeImpact.HIGH


def test_path_aware_one_to_many_correlation_and_domain_summary():
    semantic = SemanticChange(
        "Skinning", "/World/Body", "Joint weights", ChangeKind.CHANGED,
        domain="Skinning", property_path="primvars:skel:jointWeights",
        related_check_ids=("CHECK_SKIN",), source_hint="/World/Body :: weights",
    )
    previous = SimpleNamespace(results=[
        _result("CHECK_SKIN", "PASSED", "/World/Body"),
        _result("CHECK_SKIN", "FAILED", "/World/Other"),
    ])
    current = SimpleNamespace(results=[
        _result("CHECK_SKIN", "FAILED", "/World/Body"),
        _result("CHECK_SKIN", "PASSED", "/World/Other"),
    ])
    result = SimpleNamespace(changes=[semantic], validation_summary_by_domain={})
    SemanticComparisonEngine._correlate_validation(result, previous, current)
    correlations = result.changes[0].details["validation_correlation"]
    assert len(correlations) == 2
    assert correlations[0]["confidence"] == "EXACT"
    SemanticComparisonEngine._summarize_validation_by_domain(result)
    assert result.validation_summary_by_domain["Skinning"] == {"regressions": 1, "resolutions": 1}


def _result(check_id, status, location):
    return SimpleNamespace(
        check_id=check_id,
        status=SimpleNamespace(value=status),
        location=location,
    )
