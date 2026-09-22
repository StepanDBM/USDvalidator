import os
from pathlib import Path
import sys

import pytest

from s_usd_desktop.runtime.bootstrap import (
    OpenUsdBootstrapError,
    bootstrap_openusd_runtime,
    discover_openusd_runtime
)


def make_runtime(root):
    for path in (
        root / "lib/python/pxr/Usd",
        root / "lib/python/pxr/Usdviewq",
        root / "lib/python/pxr/UsdImagingGL",
        root / "plugin/usd",
        root / "bin"
    ):
        path.mkdir(parents=True, exist_ok=True)
    (root / "lib/python/pxr/Usd/__init__.py").write_text("")
    (root / "lib/python/pxr/Usdviewq/stageView.py").write_text("")
    (root / "lib/python/pxr/UsdImagingGL/__init__.py").write_text("")
    (root / "lib/usd_usdImagingGL.dll").write_bytes(b"")
    return root


def test_discovers_sibling_setup_from_project(tmp_path):
    setup = make_runtime(tmp_path / "USDs/Setup")
    project = tmp_path / "USDs/OpenUSD_Learning/lessons/USDvalidator"
    project.mkdir(parents=True)

    layout = discover_openusd_runtime(project_root=project)

    assert layout.root == setup.resolve()


def test_bootstrap_prepends_runtime_paths(tmp_path, monkeypatch):
    setup = make_runtime(tmp_path / "Setup")
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setenv("PATH", "existing")
    monkeypatch.delenv("PXR_PLUGINPATH_NAME", raising=False)
    monkeypatch.delenv("S_USDV_OPENUSD_ROOT", raising=False)

    result = bootstrap_openusd_runtime(runtime_root=setup, strict=True)

    assert result.applied is True
    assert Path(sys.path[0]) == setup / "lib/python"
    assert os.environ["PATH"].split(os.pathsep)[:2] == [
        str(setup / "lib"),
        str(setup / "bin")
    ]
    assert os.environ["PXR_PLUGINPATH_NAME"].split(os.pathsep)[0] == str(setup / "plugin/usd")
    assert os.environ["S_USDV_OPENUSD_ROOT"] == str(setup.resolve())


def test_strict_bootstrap_rejects_existing_pxr_import(monkeypatch, tmp_path):
    setup = make_runtime(tmp_path / "Setup")
    monkeypatch.setitem(sys.modules, "pxr", object())

    with pytest.raises(OpenUsdBootstrapError, match="before importing"):
        bootstrap_openusd_runtime(runtime_root=setup, strict=True)
