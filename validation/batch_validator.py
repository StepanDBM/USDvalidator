from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from time import perf_counter
import traceback

from .batch_report import BatchReport
from .publish_checker import PublishChecker


def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class BatchValidator:
    def __init__(self, checker=None, worker_count=1):
        self.checker = checker or PublishChecker()
        self.worker_count = max(1, int(worker_count))

    def validate(
        self,
        source_paths,
        cancellation_token=None,
        on_file_started=None,
        on_file_completed=None,
        on_progress=None,
    ):
        source_paths = tuple(source_paths)
        started = perf_counter()
        reports = []
        failures = []
        cancelled = False

        if self.worker_count == 1:
            for index, source_path in enumerate(source_paths, 1):
                if cancellation_token and cancellation_token.is_cancelled:
                    cancelled = True
                    break
                if on_file_started:
                    on_file_started(source_path)
                self._validate_one(source_path, reports, failures)
                if on_file_completed:
                    on_file_completed(source_path, reports[-1] if reports else None)
                if on_progress:
                    on_progress(index, len(source_paths))
        else:
            with ThreadPoolExecutor(max_workers=self.worker_count) as executor:
                futures = {}
                for source_path in source_paths:
                    if cancellation_token and cancellation_token.is_cancelled:
                        cancelled = True
                        break
                    if on_file_started:
                        on_file_started(source_path)
                    futures[executor.submit(self.checker.check, source_path)] = source_path

                completed = 0
                for future in as_completed(futures):
                    source_path = futures[future]
                    if cancellation_token and cancellation_token.is_cancelled:
                        cancelled = True
                    try:
                        report = future.result()
                        reports.append(report)
                    except Exception as exc:
                        failures.append({
                            "source_path": str(source_path).replace("\\", "/"),
                            "error": str(exc),
                            "traceback": traceback.format_exc(),
                        })
                        report = None
                    completed += 1
                    if on_file_completed:
                        on_file_completed(source_path, report)
                    if on_progress:
                        on_progress(completed, len(source_paths))

        reports.sort(key=lambda report: str(report.source_path).lower())
        return BatchReport(
            reports=reports,
            discovered_files=len(source_paths),
            cancelled=cancelled,
            started_utc=_utc_now(),
            completed_utc=_utc_now(),
            duration_seconds=round(perf_counter() - started, 6),
            failures=failures,
        )

    def _validate_one(self, source_path, reports, failures):
        try:
            reports.append(self.checker.check(source_path))
        except Exception as exc:
            failures.append({
                "source_path": str(source_path).replace("\\", "/"),
                "error": str(exc),
                "traceback": traceback.format_exc(),
            })
