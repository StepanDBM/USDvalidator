import pytest

from s_usd_desktop.cache import CachePaths, InvalidCachePathError


def test_builds_version_and_file_paths(tmp_path):
    paths = CachePaths(tmp_path)

    version_root = paths.version_root("ORB", "rover", "model", 7)
    file_path = paths.file_path("ORB", "rover", "model", 7, "root/rover.usda")

    assert version_root == tmp_path / "projects/ORB/assets/rover/streams/model/v0007"
    assert file_path == version_root / "files/root/rover.usda"


@pytest.mark.parametrize("relative_path", ["../outside.usda", "/absolute.usda", "root/../../outside.usda", ""])
def test_rejects_unsafe_relative_paths(tmp_path, relative_path):
    with pytest.raises(InvalidCachePathError):
        CachePaths(tmp_path).file_path("ORB", "rover", "model", 1, relative_path)


def test_sanitizes_catalog_components(tmp_path):
    path = CachePaths(tmp_path).version_root("ORB TEST", "hero:rover", "main model", 1)
    assert path == tmp_path / "projects/ORB_TEST/assets/hero_rover/streams/main_model/v0001"
