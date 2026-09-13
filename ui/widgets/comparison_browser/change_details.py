# ui/widgets/comparison_browser/change_details.py

import json
from html import escape

from PySide6.QtWidgets import QTextBrowser


class ChangeDetails(QTextBrowser):
    def show_change(self, change):
        if change is None:
            self.setHtml("<i>Select a semantic change to inspect it.</i>")
            return
        details = escape(json.dumps(change.details, indent=2, ensure_ascii=False, default=str))
        self.setHtml(
            f"<b>{escape(change.category)} · {escape(change.kind.value)}</b>"
            f"<h3>{escape(change.label)}</h3>"
            f"<p><b>Path:</b> {escape(change.path)}</p>"
            f"<p><b>Previous:</b> {escape(str(change.previous))}</p>"
            f"<p><b>Current:</b> {escape(str(change.current))}</p>"
            f"<h4>Details</h4><pre>{details}</pre>"
        )
