from pathlib import Path

import pytest

pytest.importorskip("PySide6")
pytest.importorskip("pxr")
from pxr import Usd

from s_usd_desktop.ui.widgets.usd_viewport.timeline import authored_time_range

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"

def test_authored_range_uses_actual_samples():
    path = FIXTURES_DIR / "animated_viewport.usda"
    stage = Usd.Stage.Open(str(path))
    assert authored_time_range(stage) == (1.0, 48.0)
