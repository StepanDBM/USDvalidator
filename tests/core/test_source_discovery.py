from pathlib import Path

from s_usd_core.batch.source_discovery import SourceDiscoveryOptions, discover_usd_files


def test_recursive_discovery_is_deterministic(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    (tmp_path / "b.usda").write_text("#usda 1.0")
    (nested / "a.usdc").write_bytes(b"")
    (nested / "ignore.txt").write_text("")

    paths = discover_usd_files(tmp_path)

    assert [path.name for path in paths] == ["b.usda", "a.usdc"]


def test_non_recursive_discovery_ignores_nested_files(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    (tmp_path / "root.usda").write_text("#usda 1.0")
    (nested / "nested.usda").write_text("#usda 1.0")

    paths = discover_usd_files(
        tmp_path,
        SourceDiscoveryOptions(recursive=False),
    )

    assert paths == ((tmp_path / "root.usda").resolve(),)


def test_discovery_applies_include_and_exclude_patterns(tmp_path):
    (tmp_path / "asset.usda").write_text("#usda 1.0")
    (tmp_path / "asset_preview.usda").write_text("#usda 1.0")
    (tmp_path / "shot.usdc").write_bytes(b"")
    options = SourceDiscoveryOptions(
        include_patterns=("*.usda",),
        exclude_patterns=("*_preview.usda",),
    )

    paths = discover_usd_files(tmp_path, options)

    assert paths == ((tmp_path / "asset.usda").resolve(),)
