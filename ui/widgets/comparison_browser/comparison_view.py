from pathlib import Path

from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from comparison.source_preflight import DiffMode, DiffScale, inspect_source_diff
from ui.dialogs.large_diff_dialog import LargeDiffDialog
from ui.workers import ComparisonWorker

from .change_details import ChangeDetails
from .diff_view import FileDiffView
from .semantic_tree import SemanticChangesTree


class ComparisonView(QWidget):
    def __init__(self, profile_loader, parent=None):
        super().__init__(parent)

        self.profile_loader = profile_loader
        self.comparison = None
        self.worker = None
        self.worker_thread = None

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        files_row = QHBoxLayout()

        previous_row, self.previous_edit, self.previous_button = self._file_row(
            "Previous:",
            self._browse_previous,
        )

        current_row, self.current_edit, self.current_button = self._file_row(
            "Current:",
            self._browse_current,
        )

        files_row.addLayout(previous_row, 1)
        files_row.addSpacing(12)
        files_row.addLayout(current_row, 1)
        files_row.addWidget(QLabel("Profile:"))

        self.profile_combo = QComboBox()
        self.profile_combo.addItems(
            self.profile_loader.get_profile_names()
        )

        files_row.addWidget(self.profile_combo)

        self.compare_button = QPushButton(
            "Compare Versions"
        )

        files_row.addWidget(self.compare_button)

        layout.addLayout(files_row)

        status_row = QHBoxLayout()

        self.summary_label = QLabel(
            "Select two USD files to compare."
        )
        self.summary_label.setMaximumHeight(42)

        self.show_unchanged = QCheckBox(
            "Show unchanged semantic values"
        )

        status_row.addWidget(self.summary_label, 1)
        status_row.addWidget(self.show_unchanged)

        layout.addLayout(status_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumHeight(18)
        self.progress_bar.hide()

        layout.addWidget(self.progress_bar)

        self.main_splitter = QSplitter(
            Qt.Orientation.Vertical
        )

        self.semantic_splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        self.semantic_tree = SemanticChangesTree()
        self.change_details = ChangeDetails()

        self.semantic_splitter.addWidget(
            self.semantic_tree
        )
        self.semantic_splitter.addWidget(
            self.change_details
        )

        self.semantic_splitter.setStretchFactor(
            0,
            2,
        )
        self.semantic_splitter.setStretchFactor(
            1,
            1,
        )

        self.diff_view = FileDiffView()

        self.main_splitter.addWidget(
            self.semantic_splitter
        )
        self.main_splitter.addWidget(
            self.diff_view
        )

        self.main_splitter.setStretchFactor(
            0,
            1,
        )
        self.main_splitter.setStretchFactor(
            1,
            1,
        )

        layout.addWidget(
            self.main_splitter,
            1,
        )

    def _connect_signals(self):
        self.compare_button.clicked.connect(
            self._compare
        )

        self.show_unchanged.toggled.connect(
            self._refresh_semantic_tree
        )

        self.semantic_tree.change_selected.connect(
            self.change_details.show_change
        )

    @staticmethod
    def _file_row(label, callback):
        layout = QHBoxLayout()

        edit = QLineEdit()
        edit.setPlaceholderText(
            "Select a USD file..."
        )

        button = QPushButton("Browse...")
        button.clicked.connect(callback)

        layout.addWidget(QLabel(label))
        layout.addWidget(edit, 1)
        layout.addWidget(button)

        return layout, edit, button

    def _browse_previous(self):
        self._browse_into(
            self.previous_edit,
            "Select Previous USD Version",
        )

    def _browse_current(self):
        self._browse_into(
            self.current_edit,
            "Select Current USD Version",
        )

    def _browse_into(self, edit, title):
        file_filter = "USD Files (*.usd *.usda *.usdc *.usdz)"

        path, selected_filter = QFileDialog.getOpenFileName(
            self,
            title,
            "",
            file_filter,
        )

        if path:
            edit.setText(path)

    def _compare(self):
        if self.worker_thread is not None:
            return

        previous = Path(
            self.previous_edit.text().strip()
        )

        current = Path(
            self.current_edit.text().strip()
        )

        if not previous.is_file() or not current.is_file():
            QMessageBox.warning(
                self,
                "Invalid Comparison",
                "Select two existing USD files.",
            )
            return

        if previous.resolve() == current.resolve():
            QMessageBox.warning(
                self,
                "Invalid Comparison",
                "Previous and current files must be different.",
            )
            return

        preflight = inspect_source_diff(previous, current)
        diff_mode = DiffMode.FULL

        if preflight.scale in {DiffScale.LARGE, DiffScale.EXTREME}:
            dialog = LargeDiffDialog(preflight, self)
            if dialog.exec() != dialog.DialogCode.Accepted:
                return
            diff_mode = dialog.selected_mode

        profile_name = self.profile_combo.currentText()

        profile = (
            self.profile_loader.get_profile(profile_name)
            if profile_name
            else None
        )

        self.comparison = None
        self.semantic_tree.clear()
        self.change_details.show_change(None)
        self.diff_view.clear()
        self._set_running(True)

        self.worker_thread = QThread(self)

        self.worker = ComparisonWorker(
            previous=previous,
            current=current,
            profile=profile,
            diff_mode=diff_mode,
        )

        self.worker.moveToThread(
            self.worker_thread
        )

        self.worker_thread.started.connect(
            self.worker.run
        )

        self.worker.phase_changed.connect(
            self._on_phase_changed
        )

        self.worker.completed.connect(
            self._on_comparison_completed
        )

        self.worker.failed.connect(
            self._on_comparison_failed
        )

        self.worker.finished.connect(
            self.worker_thread.quit
        )

        self.worker.finished.connect(
            self.worker.deleteLater
        )

        self.worker_thread.finished.connect(
            self._on_worker_finished
        )

        self.worker_thread.finished.connect(
            self.worker_thread.deleteLater
        )

        self.worker_thread.start()

    def _on_phase_changed(self, message):
        self.summary_label.setText(message)

    def _on_comparison_completed(
        self,
        comparison,
        diff_rows,
        diff_mode,
    ):
        self.comparison = comparison

        self._refresh_semantic_tree()

        if diff_mode is DiffMode.SKIP:
            self.diff_view.clear()
        else:
            self.diff_view.set_diff(diff_rows)

        self._update_summary()

        if diff_mode is DiffMode.SKIP:
            self.summary_label.setText(
                f"{self.summary_label.text()} · source diff skipped"
            )
        elif diff_mode is DiffMode.SUMMARY:
            self.summary_label.setText(
                f"{self.summary_label.text()} · summary source diff"
            )

    def _on_comparison_failed(self, message):
        self.summary_label.setText(
            "Comparison failed."
        )

        QMessageBox.critical(
            self,
            "Comparison Failed",
            message,
        )

    def _on_worker_finished(self):
        self._set_running(False)
        self.worker = None
        self.worker_thread = None

    def _set_running(self, running):
        self.previous_edit.setEnabled(
            not running
        )

        self.current_edit.setEnabled(
            not running
        )

        self.previous_button.setEnabled(
            not running
        )

        self.current_button.setEnabled(
            not running
        )

        self.profile_combo.setEnabled(
            not running
        )

        self.compare_button.setEnabled(
            not running
        )

        self.show_unchanged.setEnabled(
            not running
        )

        self.progress_bar.setVisible(
            running
        )

        if running:
            self.progress_bar.setRange(0, 0)
            self.summary_label.setText(
                "Preparing comparison..."
            )

    def _update_summary(self):
        if self.comparison is None:
            return

        changed = len(
            self.comparison.changed
        )

        regressions = sum(
            change.kind.value == "REGRESSION"
            for change in self.comparison.changes
        )

        resolved = sum(
            change.kind.value == "RESOLVED"
            for change in self.comparison.changes
        )

        additions = sum(
            change.kind.value == "ADDED"
            for change in self.comparison.changes
        )

        removals = sum(
            change.kind.value == "REMOVED"
            for change in self.comparison.changes
        )

        text = (
            f"{changed} semantic changes · "
            f"{regressions} regressions · "
            f"{resolved} resolved · "
            f"{additions} added · "
            f"{removals} removed"
        )

        warnings = " | ".join(
            self.comparison.warnings
        )

        if warnings:
            text = f"{text} · {warnings}"

        self.summary_label.setText(text)

    def _refresh_semantic_tree(self):
        if self.comparison is None:
            return

        self.semantic_tree.set_comparison(
            self.comparison,
            show_unchanged=(
                self.show_unchanged.isChecked()
            ),
        )