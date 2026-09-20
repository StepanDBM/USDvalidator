from types import SimpleNamespace

import importlib.util
from pathlib import Path

module_path = Path(__file__).parents[1] / "ui/navigation/comparison_target.py"
spec = importlib.util.spec_from_file_location("comparison_target", module_path)
module = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = module
spec.loader.exec_module(module)
resolve_comparison_target = module.resolve_comparison_target


def comparison():
    return SimpleNamespace(previous_source="previous.usda", current_source="current.usda")


def change(kind, path="", property_path="", source_hint=""):
    return SimpleNamespace(
        kind=SimpleNamespace(value=kind), path=path, property_path=property_path,
        source_hint=source_hint,
    )


def test_added_change_uses_current_source():
    target = resolve_comparison_target(comparison(), change("ADDED", "/World/AddedCube"))
    assert (target.side, target.source_path, target.prim_path) == ("current", "current.usda", "/World/AddedCube")


def test_removed_change_uses_previous_source():
    target = resolve_comparison_target(comparison(), change("REMOVED", "/World/RemovedCube"))
    assert (target.side, target.source_path, target.prim_path) == ("previous", "previous.usda", "/World/RemovedCube")


def test_property_change_selects_owning_prim():
    target = resolve_comparison_target(comparison(), change("CHANGED", "/World/ChangedCube", "/World/ChangedCube.size"))
    assert target.kind == "property"
    assert target.prim_path == "/World/ChangedCube"
    assert target.property_path == "/World/ChangedCube.size"


def test_stage_level_change_opens_current_and_has_no_target():
    target = resolve_comparison_target(comparison(), change("CHANGED", "stage.metersPerUnit"))
    assert target.side == "current"
    assert target.kind == "stage"
    assert not target.prim_path


def test_removed_stage_level_change_uses_previous():
    target = resolve_comparison_target(comparison(), change("REMOVED", "stage.defaultPrim"))
    assert target.side == "previous"
    assert target.kind == "stage"


def test_explicit_previous_side_overrides_automatic_side():
    target = resolve_comparison_target(comparison(), change("CHANGED", "/World/ChangedCube"), "previous")
    assert target.side == "previous"
    assert target.source_path == "previous.usda"


def test_source_hint_controls_automatic_side():
    target = resolve_comparison_target(comparison(), change("CHANGED", "/World/ChangedCube", source_hint="previous"))
    assert target.side == "previous"


def test_empty_path_is_stage_level_without_parser_warning():
    target = resolve_comparison_target(comparison(), change("CHANGED"))
    assert target.kind == "stage"
    assert not target.prim_path
