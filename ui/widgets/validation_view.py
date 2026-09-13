from pathlib import Path

from PySide6.QtCore import QThread
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from batch import SourceDiscoveryOptions
from reporting import ExportOptions
from ui.workers import ValidationWorker
from validation import PublishChecker

from .collapsible_panel import CollapsiblePanel
from .profile_selector import ProfileSelector
from .results_browser import ResultsBrowser
from .source_selector import SourceSelector
from .validate_button import ValidateButton


class ValidationView(QWidget):
    def __init__(
        self,
        profile_loader,
        parent=None,
    ):
        super().__init__(parent)

        self.profile_loader = profile_loader
        self.worker_thread = None
        self.worker = None

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Source, profile and validation controls
        selector_row = QHBoxLayout()

        self.source_selector = SourceSelector()
        self.profile_selector = ProfileSelector(self.profile_loader)

        self.validate_button = ValidateButton()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)

        selector_row.addWidget(self.source_selector,1)
        selector_row.addSpacing(16)
        selector_row.addWidget(self.profile_selector)
        selector_row.addSpacing(16)
        selector_row.addWidget(self.validate_button)
        selector_row.addWidget(self.cancel_button)

        layout.addLayout(selector_row)

        # Collapsible batch and export options
        options_widget = self._build_options_widget()

        self.options_panel = CollapsiblePanel(
            title="Batch and Export Options",
            content_widget=options_widget,
            expanded=False,
        )

        layout.addWidget(self.options_panel)

        # Progress
        progress_row = QHBoxLayout()

        self.current_file_label = QLabel("Idle")
        self.current_file_label.setMinimumWidth(280)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        progress_row.addWidget(self.current_file_label,1)
        progress_row.addWidget(self.progress_bar,2)

        layout.addLayout(progress_row)

        # Results
        layout.addWidget(QLabel("Results"))
        self.results_view = ResultsBrowser()

        layout.addWidget(self.results_view,1)

    def _build_options_widget(self):
        widget = QWidget()

        layout = QFormLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        self.recursive_checkbox = QCheckBox("Include subfolders")
        self.recursive_checkbox.setChecked(True)

        self.include_edit = QLineEdit()
        self.include_edit.setPlaceholderText(
            "Optional comma-separated include patterns"
        )

        self.exclude_edit = QLineEdit()
        self.exclude_edit.setPlaceholderText(
            "Optional comma-separated exclude patterns"
        )

        self.worker_count_spin = QSpinBox()
        self.worker_count_spin.setRange(1, 32)
        self.worker_count_spin.setValue(1)

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("No output directory selected")

        self.output_button = QPushButton("Browse...")

        output_row_widget = QWidget()
        output_row = QHBoxLayout(output_row_widget)
        output_row.setContentsMargins(0, 0, 0, 0)

        output_row.addWidget(self.output_edit,1)
        output_row.addWidget(self.output_button)

        self.batch_report_checkbox = (QCheckBox("Batch report"))
        self.batch_report_checkbox.setChecked(True)

        self.per_file_checkbox = QCheckBox("Per-file reports")

        self.manifest_checkbox = QCheckBox("Manifests")
        self.manifest_checkbox.setChecked(True)

        export_row_widget = QWidget()
        export_row = QHBoxLayout(export_row_widget)
        export_row.setContentsMargins(0, 0, 0, 0)

        export_row.addWidget(self.batch_report_checkbox)
        export_row.addWidget(self.per_file_checkbox)
        export_row.addWidget(self.manifest_checkbox)
        export_row.addStretch()

        layout.addRow("Discovery:", self.recursive_checkbox)
        layout.addRow("Include patterns:", self.include_edit)
        layout.addRow("Exclude patterns:", self.exclude_edit)
        layout.addRow("Worker count:", self.worker_count_spin)
        layout.addRow("Output directory:", output_row_widget)
        layout.addRow("Export:", export_row_widget)

        return widget

    def _connect_signals(self):
        self.validate_button.validate_requested.connect(self._run_validation)
        self.cancel_button.clicked.connect(self._cancel_validation)
        self.output_button.clicked.connect(self._browse_output_directory)

    def _run_validation(self):
        source_path = self.source_selector.get_source()

        if source_path is None:
            self.results_view.show_message("Select a USD file or directory first.")
            return

        profile = self.profile_selector.get_profile()

        checker = PublishChecker(profile=profile)

        discovery_options = (
            SourceDiscoveryOptions(
                recursive=self.recursive_checkbox.isChecked(),
                include_patterns=self._patterns(self.include_edit.text()),
                exclude_patterns=self._patterns(self.exclude_edit.text()),
            )
        )

        export_options = self._export_options()

        self.worker_thread = QThread(self)

        self.worker = ValidationWorker(
            source_path=source_path,
            checker=checker,
            discovery_options=discovery_options,
            worker_count=self.worker_count_spin.value(),
            export_options=export_options,
        )

        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.started.connect(self._on_started)
        self.worker.file_started.connect(self._on_file_started)
        self.worker.progress_changed.connect(self._on_progress)
        self.worker.completed.connect(self._on_completed)

        self.worker.failed.connect(self._on_failed)
        self.worker.finished.connect(self._on_finished)
        self.worker.finished.connect(self.worker_thread.quit)

        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self._set_running(True)
        self.worker_thread.start()

    def _cancel_validation(self):
        if self.worker is None:
            return

        self.current_file_label.setText("Cancelling...")

        self.cancel_button.setEnabled(False)
        self.worker.cancel()

    def _on_started(self, total):
        self.progress_bar.setRange(0, max(1, total))
        self.progress_bar.setValue(0)
        self.current_file_label.setText(f"Discovered {total} file(s)")

    def _on_file_started(self, source_path):
        self.current_file_label.setText(f"Validating: {source_path}")

    def _on_progress(self, completed, total):

        self.progress_bar.setRange(0, max(1, total))
        self.progress_bar.setValue(completed)

    def _on_completed(self, batch):
        if (
            batch.total_files == 1
            and batch.reports
        ):
            self.results_view.show_single_report(batch.reports[0])
        else:
            self.results_view.show_batch_report(batch)

        state = ("Cancelled"
            if batch.cancelled
            else "Completed"
        )

        self.current_file_label.setText(
            f"{state}: "
            f"{batch.completed_files}/"
            f"{batch.total_files} file(s)"
        )

    def _on_failed(self, message):
        self.results_view.show_message(message)
        self.current_file_label.setText("Validation failed")

    def _on_finished(self):
        self._set_running(False)
        self.worker = None
        self.worker_thread = None

    def _set_running(self, running):
        self.validate_button.setEnabled(not running)
        self.cancel_button.setEnabled(running)
        self.source_selector.setEnabled(not running)
        self.profile_selector.setEnabled(not running)
        self.options_panel.setEnabled(not running)

    def _browse_output_directory(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")

        if path:
            self.output_edit.setText(path)

    def _export_options(self):
        output_path = self.output_edit.text().strip()

        if not output_path:
            return None

        return ExportOptions(
            output_directory=Path(output_path),
            write_batch_report=self.batch_report_checkbox.isChecked(),
            write_per_file_reports=self.per_file_checkbox.isChecked(),
            write_manifests=self.manifest_checkbox.isChecked(),
        )

    @staticmethod
    def _patterns(text):
        return tuple(
            value.strip()
            for value in text.split(",")
            if value.strip()
        )

    def refresh_profiles(self):
        self.profile_selector.refresh()