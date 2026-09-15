from pathlib import Path

import pytest

pytest.importorskip("PySide6")
pytest.importorskip("pxr")
from pxr import Usd

from ui.widgets.usd_viewport.timeline import authored_time_range


def test_authored_range_uses_actual_samples():
    path = Path(__file__).parent / "fixtures/animated_viewport.usda"
    stage = Usd.Stage.Open(str(path))
    assert authored_time_range(stage) == (1.0, 48.0)
