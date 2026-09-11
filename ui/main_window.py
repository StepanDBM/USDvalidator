from pathlib import Path

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from validation import PublishChecker
from validation.batch_validator import BatchValidator
from validation.profile_loader import ProfileLoader

from .widgets.profile_selector import ProfileSelector
from .widgets.results_view import ResultsView
from .widgets.source_selector import USD_EXTENSIONS, SourceSelector
from .widgets.validate_button import ValidateButton


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("USDvalidator")
        self.resize(900, 650)

        self.profile_loader = ProfileLoader(
            "validation/profiles.json"
        )

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)

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

        self.setCentralWidget(central)

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
        checker = PublishChecker(profile=profile)

        if self.source_selector.is_file_mode():
            self._run_single(checker, source_path)
        else:
            self._run_batch(checker, source_path)

    def _run_single(self, checker, source_path):
        report = checker.check(source_path)
        self.results_view.show_single_report(report)

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

        self.results_view.show_batch_report(batch)