import pytest

PySide6 = pytest.importorskip("PySide6")
from PySide6.QtCore import QCoreApplication

from s_usd_desktop.client.models import ServiceHealth
from s_usd_desktop.services.connection_service import ConnectionService, ConnectionState
from s_usd_desktop.services.desktop_settings import ConnectionPreferences


class FakeSettings:
    def __init__(self):
        self.value = ConnectionPreferences(auto_connect=False)

    def connection_preferences(self):
        return self.value

    def set_connection_preferences(self, value):
        self.value = value


class ImmediatePool:
    def start(self, worker):
        worker.run()


@pytest.fixture(scope="module", autouse=True)
def application():
    return QCoreApplication.instance() or QCoreApplication([])


def test_successful_connection(monkeypatch):
    expected = ServiceHealth("healthy", "S-USDv Service", "0.3.0")
    monkeypatch.setattr(ConnectionService, "_check_health", staticmethod(lambda _: expected))
    service = ConnectionService(FakeSettings(), ImmediatePool())
    states = []
    service.state_changed.connect(states.append)

    service.connect_to_service()

    assert states == [ConnectionState.CONNECTING, ConnectionState.CONNECTED]
    assert service.state == ConnectionState.CONNECTED
    assert service.health == expected


def test_failed_connection(monkeypatch):
    def fail(_):
        raise RuntimeError("Offline")

    monkeypatch.setattr(ConnectionService, "_check_health", staticmethod(fail))
    service = ConnectionService(FakeSettings(), ImmediatePool())
    service.connect_to_service()

    assert service.state == ConnectionState.ERROR
    assert service.last_error == "Offline"


def test_stale_result_is_ignored():
    service = ConnectionService(FakeSettings(), ImmediatePool())
    service._generation = 2
    service._handle_connected(1, ServiceHealth("healthy", "Old", "0.1"))

    assert service.state == ConnectionState.DISCONNECTED
    assert service.health is None
