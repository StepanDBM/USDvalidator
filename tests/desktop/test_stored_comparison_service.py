import os
from types import SimpleNamespace
from uuid import uuid4

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from s_usd_desktop.services.stored_comparison_service import (
    ComparisonPairReadiness,
    StoredVersionComparisonPair,
    StoredVersionComparisonSource
)


def source(number, root_path=None, missing=0, invalid=0):
    return StoredVersionComparisonSource(
        "EXP", "probe", "model", uuid4(), number, uuid4(), root_path,
        "ready" if root_path else "root_not_cached", missing, invalid
    )


def test_pair_orders_older_as_base_and_newer_as_target():
    older = source(1, root_path="v1.usda")
    newer = source(4, root_path="v4.usda")
    pair = StoredVersionComparisonPair(
        older, newer, ComparisonPairReadiness.READY, "Ready"
    )

    assert pair.base.version_number == 1
    assert pair.target.version_number == 4
    assert pair.ready is True
    assert pair.base.display_name.endswith("v0001")
