from types import SimpleNamespace

from batch.discovery_tree import build_report_tree, common_directory


def report(path, passed=True):
    return SimpleNamespace(source_path=str(path), publish_passed=passed)


def test_common_directory_uses_shared_parent(tmp_path):
    assert common_directory([tmp_path / "A/a.usda", tmp_path / "B/b.usda"]) == tmp_path


def test_report_tree_preserves_directory_hierarchy(tmp_path):
    reports = [
        report(tmp_path / "Assets/Characters/hero.usda"),
        report(tmp_path / "Assets/Props/chair.usdc", False),
        report(tmp_path / "Shots/shot010.usda"),
    ]
    tree = build_report_tree(reports, tmp_path)
    assert set(tree.directories) == {"Assets", "Shots"}
    assert set(tree.directories["Assets"].directories) == {"Characters", "Props"}
    assert tree.file_count == 3
    assert tree.passed_count == 2
    assert tree.failed_count == 1


def test_directory_status_aggregates_descendant_results(tmp_path):
    tree = build_report_tree([
        report(tmp_path / "A/one.usda"),
        report(tmp_path / "A/two.usda", False),
    ], tmp_path)
    folder = tree.directories["A"]
    assert folder.file_count == 2
    assert folder.passed_count == 1
    assert folder.failed_count == 1


def test_empty_batch_builds_placeholder_root():
    tree = build_report_tree([])
    assert tree.name == "Batch"
    assert tree.file_count == 0
