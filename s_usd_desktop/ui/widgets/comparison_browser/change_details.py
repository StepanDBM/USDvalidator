import json
from html import escape

from PySide6.QtWidgets import QTextBrowser


class ChangeDetails(QTextBrowser):
    def show_change(self, change):
        if change is None:
            self.setHtml("<i>Select a semantic change to inspect it.</i>")
            return

        related = ", ".join(change.related_check_ids) or "None"
        validation = change.validation_consequence or self._validation_text(change.kind.value)
        details = escape(json.dumps(change.details, indent=2, ensure_ascii=False, default=str))
        self.setHtml(
            f"<b>{escape(change.domain or change.category)} · {escape(change.kind.value)} · "
            f"{escape(change.impact.value)}</b>"
            f"<h3>{escape(change.label)}</h3>"
            f"<p><b>What changed:</b> {escape(change.property_path or change.label)}</p>"
            f"<p><b>Path:</b> {escape(change.path)}</p>"
            f"<p><b>Previous value:</b> {escape(str(change.previous))}</p>"
            f"<p><b>Current value:</b> {escape(str(change.current))}</p>"
            f"<p><b>Why it matters:</b> {escape(change.why_it_matters or 'Semantic stage content changed.')}</p>"
            f"<p><b>Related validation result:</b> {escape(validation)}</p>"
            f"<p><b>Related check IDs:</b> {escape(related)}</p>"
            f"<p><b>Best-effort source location:</b> {escape(change.source_hint or change.path)}</p>"
            f"<h4>Details</h4><pre>{details}</pre>"
        )

    @staticmethod
    def _validation_text(kind):
        if kind == "REGRESSION":
            return "Validation regressed in the current publish."
        if kind == "RESOLVED":
            return "A previous validation failure was resolved."
        return "No direct validation consequence was correlated."
