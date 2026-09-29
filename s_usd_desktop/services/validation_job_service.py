from PySide6.QtCore import QObject, QThreadPool, QTimer, Signal

from s_usd_desktop.client import SUsdvApiClient, ValidationClient
from s_usd_desktop.services.workers import RequestWorker


class ValidationJobService(QObject):
    job_changed = Signal(object)
    job_finished = Signal(object)
    request_failed = Signal(str)

    def __init__(self, connection_service, interval_ms=1000, thread_pool=None, parent=None):
        super().__init__(parent)
        self.connection_service = connection_service
        self.thread_pool = thread_pool or QThreadPool.globalInstance()
        self.current_job = None
        self._workers = set()
        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self.refresh)

    def submit(self, version_id, stored_file_id, idempotency_key, profile_name="default"):
        self._submit(
            self._client_call,
            "create_job",
            version_id,
            stored_file_id,
            idempotency_key,
            profile_name,
        )

    def watch(self, job):
        self.current_job = job
        self.job_changed.emit(job)
        if job.terminal:
            self._timer.stop()
            self.job_finished.emit(job)
        else:
            self._timer.start()

    def refresh(self):
        if self.current_job and not self.current_job.terminal:
            self._submit(self._client_call, "get_job", self.current_job.id)

    def cancel(self):
        if self.current_job and not self.current_job.terminal:
            self._submit(self._client_call, "cancel_job", self.current_job.id)

    def _submit(self, function, *args):
        worker = RequestWorker(function, *args)
        worker.signals.result.connect(self.watch)
        worker.signals.error.connect(lambda error: self.request_failed.emit(str(error)))
        worker.signals.finished.connect(lambda current=worker: self._workers.discard(current))
        self._workers.add(worker)
        self.thread_pool.start(worker)

    def _client_call(self, method_name, *args):
        configuration = self.connection_service.preferences.to_api_configuration()
        with SUsdvApiClient(configuration) as api:
            return getattr(ValidationClient(api), method_name)(*args)
