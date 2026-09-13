from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from comparison.source_preflight import DiffMode, DiffScale


class LargeDiffDialog(QDialog):
    def __init__(self, preflight, parent=None):
        super().__init__(parent)
        self.preflight = preflight
        self.selected_mode = None
        self.setWindowTitle("Large Source Comparison")
        self.setMinimumWidth(520)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        line_text = (
            f"{self.preflight.total_lines:,} combined lines"
            if self.preflight.total_lines is not None
            else "an unknown number of lines"
        )
        size_mb = self.preflight.total_bytes / (1024 * 1024)
        severity = "extremely large" if self.preflight.scale is DiffScale.EXTREME else "large"
        label = QLabel(
            f"The selected source files are {severity}: {line_text}, {size_mb:,.1f} MB.\n\n"
            "Choose how the source-level diff should be handled. Semantic comparison always runs."
        )
        label.setWordWrap(True)
        layout.addWidget(label)

        self.full_button = QPushButton("Full Diff")
        self.full_button.setToolTip("Build every aligned source row. This may take considerable time and memory.")
        self.summary_button = QPushButton("Summary Diff")
        self.summary_button.setToolTip("Build changes with aggressively limited unchanged context.")
        self.skip_button = QPushButton("Skip Source Diff")
        self.skip_button.setToolTip("Run semantic comparison without source-level diffing.")
        layout.addWidget(self.full_button)
        layout.addWidget(self.summary_button)
        layout.addWidget(self.skip_button)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)
        self.full_button.clicked.connect(lambda: self._accept_mode(DiffMode.FULL))
        self.summary_button.clicked.connect(lambda: self._accept_mode(DiffMode.SUMMARY))
        self.skip_button.clicked.connect(lambda: self._accept_mode(DiffMode.SKIP))
        buttons.rejected.connect(self.reject)
        self.summary_button.setDefault(True)
        self.summary_button.setFocus()

    def _accept_mode(self, mode):
        self.selected_mode = mode
        self.accept()
