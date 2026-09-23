from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget
)


class UnavailableUsdViewportWidget(QWidget):
    validation_requested = Signal(str, bool)

    def __init__(self, capabilities, startup_error="", parent=None):
        super().__init__(parent)
        self.capabilities = capabilities
        self.startup_error = startup_error

        title = QLabel("USD Viewport Unavailable")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        description = QLabel(
            "S-USDv started without the embedded viewport because the current "
            "runtime does not satisfy every viewport capability. Validation, "
            "comparison, profiles, storage, cache, and service workflows remain "
            "available."
        )
        description.setWordWrap(True)

        reason = startup_error or "\n".join(capabilities.unavailable_reasons)
        details = QLabel(reason or "Viewport initialization was unsuccessful.")
        details.setWordWrap(True)
        details.setStyleSheet("color: #d69e2e;")

        self.diagnostics = QPlainTextEdit(capabilities.diagnostic_text())
        if startup_error:
            self.diagnostics.appendPlainText(f"\nStartup error: {startup_error}")
        self.diagnostics.setReadOnly(True)
        self.diagnostics.setMinimumHeight(220)

        copy_button = QPushButton("Copy Runtime Diagnostics")
        self.setToolTip(TooltipText.VIEWPORT_UNAVAILABLE)
        self.diagnostics.setToolTip(TooltipText.VIEWPORT_RUNTIME_DIAGNOSTICS)
        copy_button.setToolTip(TooltipText.VIEWPORT_RUNTIME_DIAGNOSTICS)
        copy_button.clicked.connect(
            lambda: QApplication.clipboard().setText(self.diagnostics.toPlainText())
        )

        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(details)
        layout.addWidget(self.diagnostics)
        layout.addWidget(copy_button)
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
