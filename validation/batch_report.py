import json
from dataclasses import dataclass, field
from pathlib import Path

from .publish_report import PublishReport
from .version import (
    BATCH_SCHEMA_NAME,
    BATCH_SCHEMA_VERSION,
    TOOL_NAME,
    TOOL_VERSION,
)


@dataclass
class BatchReport:
    reports: list[PublishReport] = field(default_factory=list)
    discovered_files: int = 0
    cancelled: bool = False
    started_utc: str = ""
    completed_utc: str = ""
    duration_seconds: float = 0.0
    failures: list[dict] = field(default_factory=list)

    @property
    def total_files(self):
        return self.discovered_files or len(self.reports)

    @property
    def completed_files(self):
        return len(self.reports) + len(self.failures)

    @property
    def remaining_files(self):
        return max(0, self.total_files - self.completed_files)

    @property
    def passed_files(self):
        return sum(report.publish_passed for report in self.reports)

    @property
    def failed_files(self):
        return sum(not report.publish_passed for report in self.reports) + len(
            self.failures
        )

    def to_dict(self):
        return {
            "schema_version": BATCH_SCHEMA_VERSION,
            "schema": {
                "name": BATCH_SCHEMA_NAME,
                "version": BATCH_SCHEMA_VERSION,
            },
            "generator": {"name": TOOL_NAME, "version": TOOL_VERSION},
            "batch": {
                "started_utc": self.started_utc,
                "completed_utc": self.completed_utc,
                "duration_seconds": self.duration_seconds,
                "cancelled": self.cancelled,
                "discovered_files": self.total_files,
                "completed_files": self.completed_files,
                "remaining_files": self.remaining_files,
                "passed_files": self.passed_files,
                "failed_files": self.failed_files,
            },
            "failures": self.failures,
            "reports": [report.to_dict() for report in self.reports],
        }

    def to_json(self, *, indent=2):
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def write_json(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")
