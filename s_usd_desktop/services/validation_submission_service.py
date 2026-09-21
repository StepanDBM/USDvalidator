from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QObject, QThreadPool, Signal

from s_usd_desktop.client import SUsdvApiClient, ValidationClient
from s_usd_desktop.services.workers import RequestWorker
from s_usd_desktop.validation import build_validation_run_payload


@dataclass(frozen=True, slots=True)
class StoredValidationTarget:
    version_id: object
    stored_file_id: object
    local_root_path: Path


class ValidationSubmissionService(QObject):
    submission_started = Signal(object)
    submission_completed = Signal(object)
    submission_failed = Signal(str)
    submission_skipped = Signal(str)
    active_changed = Signal(bool)

    def __init__(self, connection_service, thread_pool=None, parent=None):
        super().__init__(parent)
        self.connection_service = connection_service
        self.thread_pool = thread_pool or QThreadPool.globalInstance()
        self.pending_target = None
        self.worker = None

    @property
    def active(self):
        return self.worker is not None

    def expect_report(self, version_id, stored_file_id, local_root_path):
        self.pending_target = StoredValidationTarget(
            version_id,
            stored_file_id,
            Path(local_root_path).expanduser().resolve()
        )

    def clear_pending(self):
        self.pending_target = None

    def submit_matching_report(self, report):
        target = self.pending_target

        if target is None:
            return False

        report_path = Path(report.source_path).expanduser().resolve()

        if report_path != target.local_root_path:
            self.pending_target = None
            self.submission_skipped.emit(
                "Validation completed for a different source; history was not submitted."
            )
            return False

        if self.active:
            self.submission_skipped.emit(
                "A validation report submission is already in progress."
            )
            return False

        self.pending_target = None
        payload = build_validation_run_payload(report, target.stored_file_id)
        configuration = self.connection_service.preferences.to_api_configuration()
        worker = RequestWorker(
            self._create_run,
            configuration,
            target.version_id,
            payload
        )
        worker.signals.result.connect(self._completed)
        worker.signals.error.connect(self._failed)
        worker.signals.finished.connect(self._finished)
        self.worker = worker
        self.active_changed.emit(True)
        self.submission_started.emit(target)
        self.thread_pool.start(worker)
        return True

    @staticmethod
    def _create_run(configuration, version_id, payload):
        with SUsdvApiClient(configuration) as api:
            return ValidationClient(api).create_run(version_id, payload)

    def _completed(self, record):
        self.submission_completed.emit(record)

    def _failed(self, error):
        self.submission_failed.emit(getattr(error, "message", str(error)))

    def _finished(self):
        self.worker = None
        self.active_changed.emit(False)
