import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from s_usd_service.services.validation_report_payload import build_validation_run_payload


class ValidationJobExecutor:
    def __init__(self, storage):
        self.storage = storage

    def execute(self, job):
        from s_usd_core.validation import PublishChecker

        with TemporaryDirectory(prefix="s-usdv-job-") as temporary_directory:
            root = Path(temporary_directory)
            for stored_file in job.version.files:
                destination = root / Path(*Path(stored_file.relative_path).parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                with self.storage.open(stored_file.storage_key) as source, destination.open("wb") as output:
                    shutil.copyfileobj(source, output)
            source_path = root / Path(*Path(job.stored_file.relative_path).parts)
            report = PublishChecker().check(source_path)
            return build_validation_run_payload(report, job.stored_file_id)
