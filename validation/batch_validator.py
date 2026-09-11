# validation/batch_validator.py

from .publish_checker import PublishChecker
from .batch_report import BatchReport


class BatchValidator:

    def __init__(self, checker=None):
        self.checker = checker or PublishChecker()

    def validate(self, source_paths):
        reports = []

        for source_path in source_paths:
            report = self.checker.check(source_path)
            reports.append(report)

        return BatchReport(reports=reports)