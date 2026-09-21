import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings

from s_usd_desktop.cache import CacheConfiguration
from s_usd_desktop.client.models import StoredFileRecord
from s_usd_desktop.ui.storage.dialogs.cache_settings import CacheSettings
from s_usd_desktop.ui.storage.models import StoredFileTableModel

NOW = datetime.now(timezone.utc)


def stored_file():
    return StoredFileRecord(
        uuid4(), uuid4(), "root_layer", "scene.usda", "root/scene.usda",
        "objects/scene.usda", "application/octet-stream", 1536, "a" * 64,
        "available", NOW, NOW, "/content"
    )


def test_file_model_displays_cache_status():
    record = stored_file()
    model = StoredFileTableModel()
    model.set_records([record])

    assert model.data(model.index(0, 4)) == "Not cached"
    model.set_cache_status(record.id, "Cached")
    assert model.data(model.index(0, 4)) == "Cached"


def test_cache_settings_round_trip(tmp_path):
    settings_path = tmp_path / "settings.ini"
    store = CacheSettings(QSettings(str(settings_path), QSettings.IniFormat))
    expected = CacheConfiguration(
        root=tmp_path / "cache",
        maximum_bytes=25 * 1024**3,
        verify_on_access=False
    )

    store.save(expected)
    actual = store.configuration()

    assert actual == expected
