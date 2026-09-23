from s_usd_desktop.ui.tooltips import TooltipText, tooltip


def test_tooltip_catalog_is_large_unique_and_user_readable():
    entries = list(TooltipText)

    assert len(entries) >= 200
    assert len({item.name for item in entries}) == len(entries)
    assert len({item.value for item in entries}) == len(entries)
    assert all(len(item.value) >= 20 for item in entries)
    assert all(item.value.endswith((".", "?")) for item in entries)


def test_tooltip_helper_accepts_enum_and_plain_text():
    assert tooltip(TooltipText.CACHE_CONCEPT).startswith("Verified local copy")
    assert tooltip("Plain explanation.") == "Plain explanation."
