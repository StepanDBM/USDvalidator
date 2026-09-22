import os
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from s_usd_desktop.ui.storage.models import ValidationHistoryTableModel


def test_displays_validation_history_summary():
    record = SimpleNamespace(
        publish_passed=False,
        profile_name="production/default",
        total_count=13,
        failed_count=2,
        error_count=1,
        warning_count=3,
        tool_name="S-USDv",
        tool_version="0.6.0",
        completed_at=datetime(2026, 9, 22, 14, 30, tzinfo=timezone.utc)
    )
    model = ValidationHistoryTableModel()
    model.set_records([record])

    assert model.data(model.index(0, 0)) == "Failed"
    assert model.data(model.index(0, 1)) == "production/default"
    assert model.data(model.index(0, 3)) == 3
    assert model.data(model.index(0, 5)) == "S-USDv 0.6.0"
