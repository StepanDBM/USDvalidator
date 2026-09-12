from pathlib import Path

from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)

from validation import PublishChecker
from validation.batch_validator import BatchValidator

from .profile_selector import ProfileSelector
from .results_view import ResultsView
from .source_selector import USD_EXTENSIONS, SourceSelector
from .validate_button import ValidateButton


class ValidationView(QWidget):
    def __init__(self, profile_loader, parent=None):
        super().__init__(parent)

        self.profile_loader = profile_loader

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.source_selector = SourceSelector()
        layout.addWidget(self.source_selector)

        self.profile_selector = ProfileSelector(
            self.profile_loader
        )
        layout.addWidget(self.profile_selector)

        self.validate_button = ValidateButton()
        layout.addWidget(self.validate_button)

        layout.addWidget(QLabel("Results"))

        self.results_view = ResultsView()
        layout.addWidget(self.results_view, 1)

    def _connect_signals(self):
        self.validate_button.validate_requested.connect(
            self._run_validation
        )

    def _run_validation(self):
        source_path = self.source_selector.get_source()

        if source_path is None:
            self.results_view.show_message(
                "Select a USD file or directory first."
            )
            return

        profile = self.profile_selector.get_profile()

        checker = PublishChecker(
            profile=profile
        )

        if self.source_selector.is_file_mode():
            self._run_single(
                checker,
                source_path,
            )
        else:
            self._run_batch(
                checker,
                source_path,
            )

    def _run_single(self, checker, source_path):
        report = checker.check(source_path)

        self.results_view.show_single_report(
            report
        )

    def _run_batch(self, checker, source_path):
        source_paths = sorted(
            path
            for path in Path(source_path).iterdir()
            if path.is_file()
            and path.suffix.lower() in USD_EXTENSIONS
        )

        if not source_paths:
            self.results_view.show_message(
                "No supported USD files found in the selected directory."
            )
            return

        batch = BatchValidator(
            checker=checker
        ).validate(source_paths)

        self.results_view.show_batch_report(
            batch
        )

    def refresh_profiles(self):
        """
        Refresh the profile selector after profiles have been
        created, modified, or deleted by the Profile Editor.
        """
        current_name = self.profile_selector.get_profile_name()

        self.profile_selector.combo.clear()

        for name in self.profile_loader.get_profile_names():
            self.profile_selector.combo.addItem(name)

        index = self.profile_selector.combo.findText(
            current_name
        )

        if index < 0 and self.profile_selector.combo.count() > 0:
            index = 0

        if index >= 0:
            self.profile_selector.combo.setCurrentIndex(index)