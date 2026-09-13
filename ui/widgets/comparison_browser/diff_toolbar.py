from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class DiffToolbar(QWidget):
    collapse_all_requested = Signal()
    expand_all_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(6)

        self.summary_label = QLabel("No source diff")
        self.collapse_all_button = QPushButton("Collapse All")
        self.expand_all_button = QPushButton("Expand All")
        self.collapse_all_button.setEnabled(False)
        self.expand_all_button.setEnabled(False)

        layout.addWidget(self.summary_label, 1)
        layout.addWidget(self.collapse_all_button)
        layout.addWidget(self.expand_all_button)

        self.collapse_all_button.clicked.connect(self.collapse_all_requested)
        self.expand_all_button.clicked.connect(self.expand_all_requested)

    def set_summary(self, total_rows, changed_sections, unchanged_sections):
        total_sections = changed_sections + unchanged_sections
        self.summary_label.setText(
            f"{total_rows:,} rows · {changed_sections:,} changed regions · "
            f"{unchanged_sections:,} unchanged regions"
        )
        enabled = total_sections > 0
        self.collapse_all_button.setEnabled(enabled)
        self.expand_all_button.setEnabled(enabled)

    def clear(self):
        self.summary_label.setText("No source diff")
        self.collapse_all_button.setEnabled(False)
        self.expand_all_button.setEnabled(False)
