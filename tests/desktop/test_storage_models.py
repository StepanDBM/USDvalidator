import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from s_usd_desktop.client.models import ProjectRecord, StoredFileRecord, VersionRecord
from s_usd_desktop.ui.storage.models import ProjectListModel, StoredFileTableModel, VersionTableModel

NOW = datetime.now(timezone.utc)


def test_project_model_exposes_display_and_record():
    record = ProjectRecord(uuid4(), "ORB", "Orbital Workshop", "", "active", NOW, NOW)
    model = ProjectListModel()
    model.set_records([record])

    assert model.rowCount() == 1
    assert model.data(model.index(0, 0)) == "ORB  Orbital Workshop"
    assert model.record_at(0) == record


def test_version_model_formats_version_number():
    record = VersionRecord(uuid4(), uuid4(), 12, "uploaded", "Publish", NOW, NOW)
    model = VersionTableModel()
    model.set_records([record])

    assert model.data(model.index(0, 0)) == "v0012"
    assert model.data(model.index(0, 1)) == "uploaded"


def test_file_model_formats_size():
    record = StoredFileRecord(
        uuid4(), uuid4(), "root_layer", "scene.usda", "root/scene.usda",
        "objects/scene.usda", "application/octet-stream", 1536, "hash",
        "available", NOW, NOW, "/content"
    )
    model = StoredFileTableModel()
    model.set_records([record])

    assert model.data(model.index(0, 2)) == "1.5 KiB"
