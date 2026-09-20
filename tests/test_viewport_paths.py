import pytest

pytest.importorskip("pxr.Usdviewq")

from s_usd_desktop.ui.widgets.usd_viewport.stage_view_adapter import owning_prim_path


def test_owning_prim_path_accepts_prim_path():
    assert str(owning_prim_path("/World/Body")) == "/World/Body"


def test_owning_prim_path_converts_property_path():
    assert str(owning_prim_path("/World/Body.primvars:st")) == "/World/Body"


def test_owning_prim_path_rejects_non_usd_paths():
    assert owning_prim_path("C:/asset.usda") == ""
    assert owning_prim_path("") == ""
