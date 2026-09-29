import threading
from datetime import timedelta

from s_usd_service.database.models import ValidationJob
from s_usd_service.database.repositories.validation import ValidationRunRepository
from s_usd_service.database.repositories.validation_jobs import ValidationJobRepository, utc_now
from s_usd_service.database.session import SessionLocal
from s_usd_service.domain.validation_jobs import ValidationJobStatus
from s_usd_service.services.validation_job_executor import ValidationJobExecutor


class ValidationJobWorker:
    def __init__(self, storage, *, poll_seconds=1.0, retry_delay_seconds=5, session_factory=SessionLocal):
        self.storage = storage
        self.poll_seconds = poll_seconds
        self.retry_delay_seconds = retry_delay_seconds
        self.session_factory = session_factory
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self.recover_abandoned_jobs()
        self._thread = threading.Thread(target=self._run, name="s-usdv-validation-worker", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=max(2.0, self.poll_seconds * 2))

    def _run(self):
        while not self._stop_event.is_set():
            worked = self.run_once()
            if not worked:
                self._stop_event.wait(self.poll_seconds)

    def run_once(self):
        with self.session_factory() as database:
            job = ValidationJobRepository(database).claim_next()
            if not job:
                return False
            self._execute(database, job)
            return True

    def _execute(self, database, job):
        try:
            job.progress_current = 0
            job.progress_total = 1
            job.heartbeat_at = utc_now()
            database.commit()
            payload = ValidationJobExecutor(self.storage).execute(job)
            database.refresh(job)
            if job.status == ValidationJobStatus.CANCELLING.value:
                self._cancel(database, job)
                return
            run = ValidationRunRepository(database).create(job.version_id, payload, commit=False)
            database.refresh(job)
            job.validation_run_id = run.id
            job.progress_current = 1
            job.status = ValidationJobStatus.SUCCEEDED.value
            job.completed_at = utc_now()
            job.heartbeat_at = job.completed_at
            database.commit()
        except Exception as error:
            database.rollback()
            current = database.get(ValidationJob, job.id)
            if not current:
                return
            if current.status == ValidationJobStatus.CANCELLING.value:
                self._cancel(database, current)
                return
            current.error_code = type(error).__name__[:64]
            current.error_message = str(error)[:2000]
            current.heartbeat_at = utc_now()
            if current.attempt_count < current.maximum_attempts:
                current.status = ValidationJobStatus.PENDING.value
                current.next_attempt_at = utc_now() + timedelta(seconds=self.retry_delay_seconds)
            else:
                current.status = ValidationJobStatus.FAILED.value
                current.completed_at = utc_now()
            database.commit()

    @staticmethod
    def _cancel(database, job):
        now = utc_now()
        job.status = ValidationJobStatus.CANCELLED.value
        job.cancelled_at = now
        job.completed_at = now
        job.heartbeat_at = now
        database.commit()

    def recover_abandoned_jobs(self):
        with self.session_factory() as database:
            jobs = tuple(
                database.query(ValidationJob).filter(
                    ValidationJob.status.in_([ValidationJobStatus.RUNNING.value, ValidationJobStatus.CANCELLING.value])
                )
            )
            now = utc_now()
            for job in jobs:
                if job.status == ValidationJobStatus.CANCELLING.value:
                    job.status = ValidationJobStatus.CANCELLED.value
                    job.cancelled_at = now
                    job.completed_at = now
                elif job.attempt_count < job.maximum_attempts:
                    job.status = ValidationJobStatus.PENDING.value
                    job.next_attempt_at = now
                    job.error_code = "WorkerRestart"
                    job.error_message = "Job returned to the queue after service restart."
                else:
                    job.status = ValidationJobStatus.FAILED.value
                    job.completed_at = now
                    job.error_code = "WorkerRestart"
                    job.error_message = "Job exceeded its retry limit before service restart."
            database.commit()
