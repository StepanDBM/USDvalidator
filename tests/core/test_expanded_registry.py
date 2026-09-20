from s_usd_core.rules import build_registry


def test_expanded_registry_contains_all_domains():
    definitions = build_registry().all()
    categories = {item.category for item in definitions}
    assert len(definitions) == 98
    assert {"Materials", "Shaders", "Normals", "UVs", "Layers"} <= categories
