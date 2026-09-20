import json
from html import escape

from PySide6.QtWidgets import QTextBrowser


class ResultDetails(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpenExternalLinks(False)
        self.show_result(None)

    def show_result(self, result):
        if result is None:
            self.setHtml("<i>Select a validation result to inspect its details.</i>")
            return
        details = escape(
            json.dumps(result.details, indent=2, ensure_ascii=False, default=str)
        )
        rows = [
            ("Check ID", result.check_id),
            ("Label", result.label),
            ("Category", result.category),
            ("Status", result.status.value),
            ("Severity", result.severity.value),
            ("Location", result.location),
            ("Layer", result.layer),
            ("Version", result.check_version),
            ("Message", result.message),
            ("Suggestion", result.suggestion),
        ]
        body = "".join(
            f"<tr><td><b>{escape(label)}</b></td>"
            f"<td>{escape(str(value)) if value else '<i>Not provided</i>'}</td></tr>"
            for label, value in rows
        )
        self.setHtml(
            f"<table cellspacing='5'>{body}</table>"
            f"<h4>Details</h4><pre>{details}</pre>"
        )
