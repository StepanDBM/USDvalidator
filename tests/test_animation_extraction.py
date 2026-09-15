from pathlib import Path

import pytest

pxr = pytest.importorskip("pxr")
from pxr import Usd

from extraction.animation import AnimationExtractor


def test_animation_extractor_lists_properties_and_samples():
    path = Path(__file__).parent / "fixtures/animated_viewport.usda"
    result = AnimationExtractor().extract(Usd.Stage.Open(str(path)))
    item = next(value for value in result.properties if value.property_path.endswith("xformOp:translate"))
    assert item.time_samples == (1.0, 24.0, 48.0)
    assert result.time_sample_count == 3


def test_animation_fixture_has_expected_playback_range():
    path = Path(__file__).parent / "fixtures/animated_viewport.usda"
    stage = Usd.Stage.Open(str(path))
    assert stage.GetStartTimeCode() == 1
    assert stage.GetEndTimeCode() == 48
    assert stage.GetFramesPerSecond() == 24
