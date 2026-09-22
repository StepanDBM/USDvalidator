from pathlib import Path

import pytest

pytest.importorskip("PySide6")
from types import SimpleNamespace
from uuid import uuid4

from s_usd_desktop.services.stored_comparison_service import (
    ComparisonPairReadiness,
    StoredVersionComparisonPair,
    StoredVersionComparisonSource
)


def source(number, root_path=None, missing=0, invalid=0):
    return StoredVersionComparisonSource(
        "EXP",
        "probe",
        "model",
        uuid4(),
        number,
        uuid4(),
        Path(root_path) if root_path else None,
        "ready" if root_path else "root_not_cached",
        missing,
        invalid
    )


def test_prepared_pair_exposes_verified_root_paths():
    base = source(1, "C:/cache/v0001/root/probe.usda")
    target = source(2, "C:/cache/v0002/root/probe.usda")
    pair = StoredVersionComparisonPair(
        base,
        target,
        ComparisonPairReadiness.READY,
        "Ready"
    )

    assert pair.ready is True
    assert pair.base.root_path.name == "probe.usda"
    assert pair.target.root_path.name == "probe.usda"
    assert pair.base.location.version_number == 1
    assert pair.target.location.version_number == 2


def test_uncached_pair_requires_preparation():
    pair = StoredVersionComparisonPair(
        source(1, missing=1),
        source(2, "C:/cache/v0002/root/probe.usda"),
        ComparisonPairReadiness.PREPARATION_REQUIRED,
        "Preparation required"
    )

    assert pair.ready is False
    assert pair.base.missing_count == 1
