from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class UnavailableUsdViewportWidget(QWidget):
    validation_requested = Signal(str, bool)

    def __init__(self, reason="", parent=None):
        super().__init__(parent)

        title = QLabel("USD Viewport Unavailable")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        description = QLabel(
            "The installed OpenUSD runtime does not include pxr.Usdviewq, "
            "which S-USDv currently uses for the embedded viewport.\n\n"
            "Validation, comparison, profiles, storage, and service "
            "connectivity remain available."
        )
        description.setWordWrap(True)

        details = QLabel(reason)
        details.setWordWrap(True)
        details.setTextInteractionFlags(details.textInteractionFlags())
        details.setStyleSheet("color: #d69e2e;")

        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(details)
        layout.addStretch()

    def shutdown(self):
        pass

    def retry_pending_validation(self):
        pass

    def set_validation_report(self, _report):
        pass

    def defer_validation(self, _source_path, _force=False):
        pass

    def show_validation_result(self, _report, _result):
        pass

    def show_comparison_change(self, _comparison, _change, _side):
        pass