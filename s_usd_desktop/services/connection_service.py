from enum import Enum

from PySide6.QtCore import QObject, QThreadPool, Signal

from s_usd_desktop.client import CatalogClient, SUsdvApiClient
from s_usd_desktop.client.errors import SUsdvClientError
from s_usd_desktop.services.desktop_settings import DesktopSettings
from s_usd_desktop.services.workers import RequestWorker


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class ConnectionService(QObject):
    state_changed = Signal(object)
    connected = Signal(object)
    disconnected = Signal()
    connection_failed = Signal(str)

    def __init__(self, settings=None, thread_pool=None, parent=None):
        super().__init__(parent)
        self.settings = settings or DesktopSettings()
        self.thread_pool = thread_pool or QThreadPool.globalInstance()
        self.state = ConnectionState.DISCONNECTED
        self.health = None
        self.last_error = ""
        self._generation = 0
        self._workers = set()

    @property
    def preferences(self):
        return self.settings.connection_preferences()

    def connect_to_service(self):
        if self.state == ConnectionState.CONNECTING:
            return

        self._generation += 1
        generation = self._generation
        configuration = self.preferences.to_api_configuration()
        self.health = None
        self.last_error = ""
        self._set_state(ConnectionState.CONNECTING)
        worker = RequestWorker(self._check_health, configuration)
        worker.signals.result.connect(
            lambda health, current=generation: self._handle_connected(current, health)
        )
        worker.signals.error.connect(
            lambda error, current=generation: self._handle_error(current, error)
        )
        worker.signals.finished.connect(lambda current=worker: self._workers.discard(current))
        self._workers.add(worker)
        self.thread_pool.start(worker)

    def refresh(self):
        self.connect_to_service()

    def disconnect_from_service(self):
        self._generation += 1
        self.health = None
        self.last_error = ""
        self._set_state(ConnectionState.DISCONNECTED)
        self.disconnected.emit()

    def apply_preferences(self, preferences, reconnect=True):
        preferences.to_api_configuration()
        self.settings.set_connection_preferences(preferences)

        if reconnect:
            self.disconnect_from_service()
            self.connect_to_service()

    @staticmethod
    def _check_health(configuration):
        with SUsdvApiClient(configuration) as api:
            return CatalogClient(api).get_health()

    def _handle_connected(self, generation, health):
        if generation != self._generation:
            return

        self.health = health
        self.last_error = ""
        self._set_state(ConnectionState.CONNECTED)
        self.connected.emit(health)

    def _handle_error(self, generation, error):
        if generation != self._generation:
            return

        self.health = None
        self.last_error = error.message if isinstance(error, SUsdvClientError) else str(error)
        self._set_state(ConnectionState.ERROR)
        self.connection_failed.emit(self.last_error)

    def _set_state(self, state):
        if self.state == state:
            return

        self.state = state
        self.state_changed.emit(state)
