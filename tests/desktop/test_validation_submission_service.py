import os
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")
from PySide6.QtCore import QCoreApplication

from s_usd_core.validation.publish_report import PublishReport
from s_usd_desktop.services.validation_submission_service import ValidationSubmissionService


class Preferences:
    def to_api_configuration(self):
        return object()


class Connection:
    preferences = Preferences()


class ImmediatePool:
    def start(self, worker):
        worker.run()


@pytest.fixture(scope="module", autouse=True)
def application():
    return QCoreApplication.instance() or QCoreApplication([])


def report(path):
    return PublishReport(str(path), True, str(path))


def test_submits_only_matching_pending_report(tmp_path, monkeypatch):
    path = tmp_path / "root.usda"
    path.write_text("#usda 1.0")
    service = ValidationSubmissionService(Connection(), ImmediatePool())
    version_id = uuid4()
    file_id = uuid4()
    expected = SimpleNamespace(id=uuid4())
    captured = {}

    def create(_configuration, submitted_version_id, payload):
        captured["version_id"] = submitted_version_id
        captured["payload"] = payload
        return expected

    monkeypatch.setattr(service, "_create_run", create)
    completed = []
    service.submission_completed.connect(completed.append)
    service.expect_report(version_id, file_id, path)

    assert service.submit_matching_report(report(path)) is True
    assert captured["version_id"] == version_id
    assert captured["payload"]["stored_file_id"] == str(file_id)
    assert completed == [expected]
    assert service.pending_target is None


def test_mismatched_source_is_not_submitted(tmp_path, monkeypatch):
    expected_path = tmp_path / "expected.usda"
    other_path = tmp_path / "other.usda"
    service = ValidationSubmissionService(Connection(), ImmediatePool())
    service.expect_report(uuid4(), uuid4(), expected_path)
    called = []
    monkeypatch.setattr(service, "_create_run", lambda *args: called.append(args))

    assert service.submit_matching_report(report(other_path)) is False
    assert called == []
    assert service.pending_target is None


def test_manual_validation_without_pending_target_is_ignored(tmp_path):
    service = ValidationSubmissionService(Connection(), ImmediatePool())

    assert service.submit_matching_report(report(tmp_path / "manual.usda")) is False
