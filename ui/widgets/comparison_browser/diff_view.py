from html import escape

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QHBoxLayout, QLabel, QTextBrowser, QVBoxLayout, QWidget


COLORS = {
    "UNCHANGED": "transparent",
    "REMOVED": "rgba(248, 81, 73, 0.25)",
    "ADDED": "rgba(46, 160, 67, 0.30)",
    "CHANGED": "rgba(210, 153, 34, 0.28)",
}


class FileDiffView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.old_browser = self._panel(layout, "Previous")
        self.new_browser = self._panel(layout, "Current")
        self.old_browser.verticalScrollBar().valueChanged.connect(
            self.new_browser.verticalScrollBar().setValue
        )
        self.new_browser.verticalScrollBar().valueChanged.connect(
            self.old_browser.verticalScrollBar().setValue
        )

    def _panel(self, parent_layout, title):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(title))
        browser = QTextBrowser()
        browser.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        browser.setLineWrapMode(QTextBrowser.LineWrapMode.NoWrap)
        layout.addWidget(browser, 1)
        parent_layout.addWidget(widget, 1)
        return browser

    def set_diff(self, rows):
        self.old_browser.setHtml(self._html(rows, old=True))
        self.new_browser.setHtml(self._html(rows, old=False))

    @staticmethod
    def _html(rows, old):
        lines = []
        for row in rows:
            number = row.old_number if old else row.new_number
            text = row.old_text if old else row.new_text
            visible_kind = row.kind
            if row.kind == "ADDED" and old:
                visible_kind = "UNCHANGED"
            elif row.kind == "REMOVED" and not old:
                visible_kind = "UNCHANGED"
            prefix = "-" if old and row.kind in {"REMOVED", "CHANGED"} else "+" if not old and row.kind in {"ADDED", "CHANGED"} else " "
            lines.append(
                f'<div style="white-space: pre; background: {COLORS[visible_kind]};">'
                f'<span style="color:#8b949e; display:inline-block; width:48px;">'
                f'{number if number is not None else ""}</span>'
                f'<span style="display:inline-block; width:18px;">{prefix}</span>'
                f'{escape(text) or "&nbsp;"}</div>'
            )
        return "<html><body style='margin:0;'>" + "".join(lines) + "</body></html>"
