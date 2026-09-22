from collections import defaultdict

from PySide6.QtCore import QObject, QThreadPool, Signal

from s_usd_desktop.client import SUsdvApiClient, ValidationClient
from s_usd_desktop.services.workers import RequestWorker


class ValidationHistoryService(QObject):
    history_loaded = Signal(object, object)
    run_loaded = Signal(object)
    loading_changed = Signal(str, bool)
    request_failed = Signal(str, str)

    def __init__(self, connection_service, thread_pool=None, parent=None):
        super().__init__(parent)
        self.connection_service = connection_service
        self.thread_pool = thread_pool or QThreadPool.globalInstance()
        self._generations = defaultdict(int)
        self._workers = set()

    @property
    def active(self):
        return bool(self._workers)

    def invalidate(self, *scopes):
        for scope in scopes:
            self._generations[scope] += 1

    def load_history(self, version_id):
        self._submit("history", self.history_loaded, "list_runs", version_id, context=version_id)

    def load_run(self, run_id):
        self._submit("run", self.run_loaded, "get_run", run_id)

    def _submit(self, scope, signal, method_name, *args, context=None):
        self._generations[scope] += 1
        generation = self._generations[scope]
        self.loading_changed.emit(scope, True)
        worker = RequestWorker(self._call, method_name, *args)
        worker.signals.result.connect(
            lambda result, s=scope, g=generation, c=context: self._result(
                s, g, c, result, signal
            )
        )
        worker.signals.error.connect(
            lambda error, s=scope, g=generation: self._error(s, g, error)
        )
        worker.signals.finished.connect(
            lambda current=worker: self._workers.discard(current)
        )
        self._workers.add(worker)
        self.thread_pool.start(worker)

    def _call(self, method_name, *args):
        configuration = self.connection_service.preferences.to_api_configuration()
        with SUsdvApiClient(configuration) as api:
            return getattr(ValidationClient(api), method_name)(*args)

    def _result(self, scope, generation, context, result, signal):
        if generation != self._generations[scope]:
            return

        self.loading_changed.emit(scope, False)

        if context is None:
            signal.emit(result)
        else:
            signal.emit(context, result)

    def _error(self, scope, generation, error):
        if generation != self._generations[scope]:
            return

        self.loading_changed.emit(scope, False)
        self.request_failed.emit(scope, getattr(error, "message", str(error)))
