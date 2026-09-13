from html import escape

from PySide6.QtWidgets import QTextEdit


PASSED_COLOR = "#4CAF50"
FAILED_COLOR = "#F44336"
TEXT_COLOR = "#D8D8D8"
MUTED_COLOR = "#A0A0A0"


class ResultsView(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)

    def show_single_report(self, report):
        status = "PASSED" if report.publish_passed else "FAILED"
        status_html = self._status_html(status)

        lines = [
            f"<b>Status:</b> {status_html}",
            f"<b>Source:</b> {escape(str(report.source_path))}",
            f"<b>Checks:</b> {report.summary.total}",
            f"<b>Passed:</b> {report.summary.passed}",
            f"<b>Failed:</b> {report.summary.failed}",
            f"<b>Skipped:</b> {report.summary.skipped}",
            "",
        ]

        lines.extend(
            (
                f"{self._status_html(result.status.value)} "
                f"<b>{escape(result.check_id)}</b>: "
                f"{escape(result.message)}"
            )
            for result in report.results
        )

        self.setHtml("<br>".join(lines))

    def show_batch_report(self, batch):
        lines = [
            "<b>Batch Validation</b>",
            "",
            f"<b>Files:</b> {batch.total_files}",
            f"<b>Passed:</b> {batch.passed_files}",
            f"<b>Failed:</b> {batch.failed_files}",
            "",
        ]

        lines.extend(
            (
                f"{self._status_html('PASSED' if report.publish_passed else 'FAILED')} "
                f"{escape(str(report.source_path))}"
            )
            for report in batch.reports
        )

        self.setHtml("<br>".join(lines))

    def show_message(self, message):
        self.setHtml(escape(str(message)).replace("\n", "<br>"))

    def clear_results(self):
        self.clear()

    @staticmethod
    def _status_html(status):
        status = str(status).upper()

        if status == "PASSED":
            color = PASSED_COLOR
        elif status in {"FAILED", "ERROR"}:
            color = FAILED_COLOR
        else:
            color = MUTED_COLOR

        return (
            f'<span style="color: {color}; font-weight: 600;">'
            f'[{escape(status)}]'
            "</span>"
        )