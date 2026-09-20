from pathlib import Path

from s_usd_core.comparison import ChangeKind, SemanticComparisonEngine, build_side_by_side_diff


FIXTURES = Path(__file__).parent / "fixtures"


def test_semantic_comparison_finds_hierarchy_geometry_and_animation_changes():
    comparison = SemanticComparisonEngine().compare(
        FIXTURES / "comparison_previous.usda",
        FIXTURES / "comparison_current.usda",
    )
    changes = {(item.category, item.path, item.kind) for item in comparison.changes}

    assert ("Hierarchy", "/World/OldProp", ChangeKind.REMOVED) in changes
    assert ("Hierarchy", "/World/NewProp", ChangeKind.ADDED) in changes
    assert any(
        item.category == "Geometry"
        and item.path == "/World/Body.points_count"
        and item.kind is ChangeKind.INCREASED
        for item in comparison.changes
    )
    assert any(
        item.category == "Animation"
        and item.path.startswith("/World/NewProp.xformOp:translate")
        and item.kind is ChangeKind.ADDED
        for item in comparison.changes
    )


def test_text_diff_contains_added_and_removed_rows():
    rows = build_side_by_side_diff(
        FIXTURES / "comparison_previous.usda",
        FIXTURES / "comparison_current.usda",
    )

    assert any(row.kind in {"REMOVED", "CHANGED"} for row in rows)
    assert any(row.kind in {"ADDED", "CHANGED"} for row in rows)
