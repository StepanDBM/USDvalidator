from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from comparison import SemanticComparisonEngine, build_side_by_side_diff

from .change_details import ChangeDetails
from .diff_view import FileDiffView
from .semantic_tree import SemanticChangesTree


class ComparisonView(QWidget):
    def __init__(self, profile_loader, parent=None):
        super().__init__(parent)
        self.profile_loader = profile_loader
        self.comparison = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        old_row = self._file_row("Previous:", self._browse_previous)
        self.previous_edit, self.previous_button = old_row[1], old_row[2]
        new_row = self._file_row("Current:", self._browse_current)
        self.current_edit, self.current_button = new_row[1], new_row[2]
        files_row = QHBoxLayout()
        files_row.addLayout(old_row[0], 1)
        files_row.addSpacing(12)
        files_row.addLayout(new_row[0], 1)
        files_row.addWidget(QLabel("Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(self.profile_loader.get_profile_names())
        files_row.addWidget(self.profile_combo)
        self.compare_button = QPushButton("Compare Versions")
        files_row.addWidget(self.compare_button)
        layout.addLayout(files_row)

        summary_row = QHBoxLayout()
        self.summary_label = QLabel("Select two USD files to compare.")
        self.summary_label.setMaximumHeight(42)
        self.show_unchanged = QCheckBox("Show unchanged semantic values")
        summary_row.addWidget(self.summary_label, 1)
        summary_row.addWidget(self.show_unchanged)
        layout.addLayout(summary_row)

        vertical = QSplitter(Qt.Orientation.Vertical)
        semantic_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.semantic_tree = SemanticChangesTree()
        self.change_details = ChangeDetails()
        semantic_splitter.addWidget(self.semantic_tree)
        semantic_splitter.addWidget(self.change_details)
        semantic_splitter.setStretchFactor(0, 2)
        semantic_splitter.setStretchFactor(1, 1)
        self.diff_view = FileDiffView()
        vertical.addWidget(semantic_splitter)
        vertical.addWidget(self.diff_view)
        vertical.setStretchFactor(0, 1)
        vertical.setStretchFactor(1, 1)
        layout.addWidget(vertical, 1)

        self.compare_button.clicked.connect(self._compare)
        self.show_unchanged.toggled.connect(self._refresh_semantic_tree)
        self.semantic_tree.change_selected.connect(self.change_details.show_change)

    @staticmethod
    def _file_row(label, callback):
        layout = QHBoxLayout()
        edit = QLineEdit()
        edit.setPlaceholderText("Select a USD file...")
        button = QPushButton("Browse...")
        button.clicked.connect(callback)
        layout.addWidget(QLabel(label))
        layout.addWidget(edit, 1)
        layout.addWidget(button)
        return layout, edit, button

    def _browse_previous(self):
        self._browse_into(self.previous_edit, "Select Previous USD Version")

    def _browse_current(self):
        self._browse_into(self.current_edit, "Select Current USD Version")

    def _browse_into(self, edit, title):
        path, _ = QFileDialog.getOpenFileName(
            self, title, "", "USD Files (*.usd *.usda *.usdc *.usdz)"
        )
        if path:
            edit.setText(path)

    def _compare(self):
        previous = Path(self.previous_edit.text().strip())
        current = Path(self.current_edit.text().strip())
        if not previous.is_file() or not current.is_file():
            QMessageBox.warning(self, "Invalid Comparison", "Select two existing USD files.")
            return
        try:
            profile_name = self.profile_combo.currentText()
            profile = self.profile_loader.get_profile(profile_name) if profile_name else None
            self.comparison = SemanticComparisonEngine(profile=profile).compare(previous, current)
            rows = build_side_by_side_diff(previous, current)
        except Exception as exc:
            QMessageBox.critical(self, "Comparison Failed", str(exc))
            return
        self._refresh_semantic_tree()
        self.diff_view.set_diff(rows)
        changed = len(self.comparison.changed)
        regressions = self.comparison.count_kind("REGRESSION") if hasattr(self.comparison, "count_kind") else sum(c.kind.value == "REGRESSION" for c in self.comparison.changes)
        resolved = sum(c.kind.value == "RESOLVED" for c in self.comparison.changes)
        warnings = " | ".join(self.comparison.warnings)
        text = f"{changed} semantic changes · {regressions} regressions · {resolved} resolved"
        self.summary_label.setText(f"{text} · {warnings}" if warnings else text)

    def _refresh_semantic_tree(self):
        if self.comparison:
            self.semantic_tree.set_comparison(
                self.comparison,
                show_unchanged=self.show_unchanged.isChecked(),
            )
