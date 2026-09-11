from PySide6.QtWidgets import QTextEdit


class ResultsView(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setReadOnly(True)

    def show_single_report(self, report):
        status = "PASSED" if report.publish_passed else "FAILED"

        lines = [
            f"Status: {status}",
            f"Source: {report.source_path}",
            f"Checks: {report.summary.total}",
            f"Passed: {report.summary.passed}",
            f"Failed: {report.summary.failed}",
            f"Skipped: {report.summary.skipped}",
            "",
        ]

        lines.extend(
            (
                f"[{result.status.value}] "
                f"{result.check_id}: "
                f"{result.message}"
            )
            for result in report.results
        )

        self.setPlainText("\n".join(lines))

    def show_batch_report(self, batch):
        lines = [
            "Batch Validation",
            "",
            f"Files: {batch.total_files}",
            f"Passed: {batch.passed_files}",
            f"Failed: {batch.failed_files}",
            "",
        ]

        lines.extend(
            f"[{'PASS' if report.publish_passed else 'FAIL'}] "
            f"{report.source_path}"
            for report in batch.reports
        )

        self.setPlainText("\n".join(lines))

    def show_message(self, message):
        self.setPlainText(message)

    def clear_results(self):
        self.clear()