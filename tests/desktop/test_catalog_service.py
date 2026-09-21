import pytest

pytest.importorskip("PySide6")
from PySide6.QtCore import QCoreApplication

from s_usd_desktop.services.catalog_service import CatalogService


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


def test_ignores_stale_results():
    pool = DeferredPool()
    service = CatalogService(Connection(), pool)
    received = []
    service.projects_loaded.connect(received.append)
    service._catalog_call = lambda *_: ("current",)
    service.load_projects()
    first = pool.workers[-1]
    service.load_projects()
    second = pool.workers[-1]

    first.run()
    second.run()

    assert received == [("current",)]
