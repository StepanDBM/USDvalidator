import json
from dataclasses import dataclass, field
from pathlib import Path

from .publish_report import PublishReport


BATCH_REPORT_SCHEMA_VERSION = "1.0"


@dataclass
class BatchReport:
    reports: list[PublishReport] = field(default_factory=list)

    @property
    def total_files(self):
        return len(self.reports)

    @property
    def passed_files(self):
        return sum(
            report.publish_passed
            for report in self.reports
        )

    @property
    def failed_files(self):
        return sum(
            not report.publish_passed
            for report in self.reports
        )

    def to_dict(self):
        return {
            "schema_version": BATCH_REPORT_SCHEMA_VERSION,
            "batch": {
                "total_files": self.total_files,
                "passed_files": self.passed_files,
                "failed_files": self.failed_files,
            },
            "reports": [
                report.to_dict()
                for report in self.reports
            ],
        }

    def to_json(self, *, indent=2):
        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=False,
        )

    def write_json(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            self.to_json(),
            encoding="utf-8",
        )