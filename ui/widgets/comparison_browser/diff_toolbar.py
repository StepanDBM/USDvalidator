from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QPushButton, QWidget


class DiffToolbar(QWidget):
    previous_requested = Signal()
    next_requested = Signal()
    changes_only_toggled = Signal(bool)
    collapse_all_requested = Signal()
    expand_all_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(6)
        self.previous_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.counter_label = QLabel("No changes")
        self.changes_only_check = QCheckBox("Changes only")
        self.summary_label = QLabel("No source diff")
        self.collapse_all_button = QPushButton("Collapse All")
        self.expand_all_button = QPushButton("Expand All")
        layout.addWidget(self.previous_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.counter_label)
        layout.addWidget(self.changes_only_check)
        layout.addWidget(self.summary_label, 1)
        layout.addWidget(self.collapse_all_button)
        layout.addWidget(self.expand_all_button)
        self.previous_button.clicked.connect(self.previous_requested)
        self.next_button.clicked.connect(self.next_requested)
        self.changes_only_check.toggled.connect(self.changes_only_toggled)
        self.collapse_all_button.clicked.connect(self.collapse_all_requested)
        self.expand_all_button.clicked.connect(self.expand_all_requested)
        self.clear()

    def set_summary(self, result, change_count, changed_sections, unchanged_sections):
        mode = result.mode.value.title()
        generated = len(result.rows)
        omitted = result.omitted_total
        suffix = f" · {omitted:,} source rows omitted" if omitted else ""
        self.summary_label.setText(
            f"{mode} Diff · {generated:,} generated rows{suffix} · "
            f"{changed_sections:,} large changed · {unchanged_sections:,} large unchanged"
        )
        has_changes = change_count > 0
        has_sections = changed_sections + unchanged_sections > 0
        self.previous_button.setEnabled(has_changes)
        self.next_button.setEnabled(has_changes)
        self.changes_only_check.setEnabled(has_changes)
        self.collapse_all_button.setEnabled(has_sections)
        self.expand_all_button.setEnabled(has_sections)
        self.set_counter(-1, change_count)

    def set_counter(self, current, total):
        if current >= 0 and total:
            self.counter_label.setText(f"Change {current + 1} of {total}")
        else:
            self.counter_label.setText(f"{total} changes" if total else "No changes")

    def clear(self, text="No source diff"):
        self.summary_label.setText(text)
        self.counter_label.setText("No changes")
        self.changes_only_check.blockSignals(True)
        self.changes_only_check.setChecked(False)
        self.changes_only_check.blockSignals(False)
        for widget in (
            self.previous_button,
            self.next_button,
            self.changes_only_check,
            self.collapse_all_button,
            self.expand_all_button,
        ):
            widget.setEnabled(False)
