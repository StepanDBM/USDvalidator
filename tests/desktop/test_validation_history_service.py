import os
from types import SimpleNamespace
from uuid import uuid4

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")
from PySide6.QtCore import QCoreApplication

from s_usd_desktop.services.validation_history_service import ValidationHistoryService


class Preferences:
    def to_api_configuration(self):
        return object()


class Connection:
    preferences = Preferences()


class DeferredPool:
    def __init__(self):
        self.workers = []

    def start(self, worker):
        self.workers.append(worker)


@pytest.fixture(scope="module", autouse=True)
def application():
    return QCoreApplication.instance() or QCoreApplication([])


def test_ignores_stale_history_results(monkeypatch):
    pool = DeferredPool()
    service = ValidationHistoryService(Connection(), pool)
    version_id = uuid4()
    received = []
    service.history_loaded.connect(lambda context, records: received.append((context, records)))
    monkeypatch.setattr(service, "_call", lambda *_: ("latest",))

    service.load_history(version_id)
    first = pool.workers[-1]
    service.load_history(version_id)
    second = pool.workers[-1]
    first.run()
    second.run()

    assert received == [(version_id, ("latest",))]


def test_run_detail_emits_record(monkeypatch):
    pool = DeferredPool()
    service = ValidationHistoryService(Connection(), pool)
    expected = SimpleNamespace(id=uuid4())
    monkeypatch.setattr(service, "_call", lambda *_: expected)
    received = []
    service.run_loaded.connect(received.append)

    service.load_run(expected.id)
    pool.workers[-1].run()

    assert received == [expected]
