from ui.widgets.profile_editor import ProfileDraft
from validation.attribute_override import AttributeOverride
from validation.profiles import ValidationProfile


def test_profile_draft_preserves_overrides():
    profile = ValidationProfile(
        name="heavy_geometry",
        overrides=(
            AttributeOverride(
                path="geometry.polygon_count_limit",
                value=200000,
            ),
        ),
    )

    draft = ProfileDraft.from_profile(profile)
    rebuilt_profile = draft.to_profile()

    assert rebuilt_profile.overrides == profile.overrides


def test_profile_draft_adds_override():
    draft = ProfileDraft(
        name="heavy_geometry",
        description="",
    )

    draft.set_override(
        path="geometry.polygon_count_limit",
        value=200000,
    )

    override = draft.get_override(
        "geometry.polygon_count_limit"
    )

    assert override.value == 200000
    assert override.enabled is True


def test_profile_draft_replaces_override():
    draft = ProfileDraft(
        name="heavy_geometry",
        description="",
        overrides=[
            AttributeOverride(
                path="geometry.polygon_count_limit",
                value=100000,
            ),
        ],
    )

    draft.set_override(
        path="geometry.polygon_count_limit",
        value=200000,
    )

    assert len(draft.overrides) == 1
    assert draft.overrides[0].value == 200000


def test_profile_draft_removes_override():
    draft = ProfileDraft(
        name="heavy_geometry",
        description="",
        overrides=[
            AttributeOverride(
                path="geometry.polygon_count_limit",
                value=200000,
            ),
        ],
    )

    draft.remove_override(
        "geometry.polygon_count_limit"
    )

    assert draft.overrides == []