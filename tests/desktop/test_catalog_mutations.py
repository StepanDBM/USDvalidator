import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")
from PySide6.QtCore import QCoreApplication

from s_usd_desktop.services.catalog_service import CatalogService


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


def test_create_project_emits_result(monkeypatch):
    service = CatalogService(Connection(), ImmediatePool())
    monkeypatch.setattr(service, "_catalog_call", lambda *args: args)
    results = []
    service.project_created.connect(results.append)

    service.create_project("ORB", "Orbital Workshop", "Test")

    assert results == [("create_project", "ORB", "Orbital Workshop", "Test")]
