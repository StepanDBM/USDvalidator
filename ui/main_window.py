from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
    QTextEdit,
)

from validation import PublishChecker
from validation.batch_validator import BatchValidator
from validation.profile_loader import ProfileLoader
from validation.profiles import DEFAULT_PROFILE


USD_EXTENSIONS = {".usd", ".usda", ".usdc", ".usdz"}


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("USDvalidator")
        self.resize(900, 650)

        self.source_path = None

        self.profile_loader = ProfileLoader(
            "validation/profiles.json"
        )

        self._build_ui()
        self._load_profiles()

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)

        # Source
        layout.addWidget(QLabel("Source"))

        source_layout = QHBoxLayout()

        self.source_label = QLabel("No file or folder selected")
        self.source_label.setWordWrap(True)

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_source)

        source_layout.addWidget(self.source_label, 1)
        source_layout.addWidget(browse_button)

        layout.addLayout(source_layout)

        # Mode
        mode_layout = QHBoxLayout()

        mode_layout.addWidget(QLabel("Mode:"))

        self.file_radio = QRadioButton("File")
        self.folder_radio = QRadioButton("Folder")

        self.file_radio.setChecked(True)

        mode_layout.addWidget(self.file_radio)
        mode_layout.addWidget(self.folder_radio)
        mode_layout.addStretch()

        layout.addLayout(mode_layout)

        # Profile
        layout.addWidget(QLabel("Profile"))

        self.profile_combo = QComboBox()
        layout.addWidget(self.profile_combo)

        # Run
        self.run_button = QPushButton("Run Validation")
        self.run_button.clicked.connect(self._run_validation)

        layout.addWidget(self.run_button)

        # Results
        layout.addWidget(QLabel("Results"))

        self.results_output = QTextEdit()
        self.results_output.setReadOnly(True)

        layout.addWidget(self.results_output, 1)

        self.setCentralWidget(central)

    def _load_profiles(self):
        for name in self.profile_loader.get_profile_names():
            self.profile_combo.addItem(name)

        index = self.profile_combo.findText(DEFAULT_PROFILE)

        if index >= 0:
            self.profile_combo.setCurrentIndex(index)

    def _browse_source(self):
        if self.file_radio.isChecked():
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Select USD File",
                "",
                "USD Files (*.usd *.usda *.usdc *.usdz)",
            )

            if not path:
                return

        else:
            path = QFileDialog.getExistingDirectory(
                self,
                "Select USD Directory",
            )

            if not path:
                return

        self.source_path = Path(path)
        self.source_label.setText(str(self.source_path))

    def _run_validation(self):
        if self.source_path is None:
            self.results_output.setPlainText(
                "Select a USD file or directory first."
            )
            return

        profile_name = self.profile_combo.currentText()
        profile = self.profile_loader.get_profile(profile_name)

        checker = PublishChecker(profile=profile)

        if self.file_radio.isChecked():
            self._run_single(checker)
        else:
            self._run_batch(checker)

    def _run_single(self, checker):
        report = checker.check(self.source_path)

        status = "PASSED" if report.publish_passed else "FAILED"

        self.results_output.setPlainText(
            "\n".join(
                [
                    f"Status: {status}",
                    f"Source: {report.source_path}",
                    f"Checks: {report.summary.total}",
                    f"Passed: {report.summary.passed}",
                    f"Failed: {report.summary.failed}",
                    f"Skipped: {report.summary.skipped}",
                    "",
                    *[
                        (
                            f"[{result.status.value}] "
                            f"{result.check_id}: "
                            f"{result.message}"
                        )
                        for result in report.results
                    ],
                ]
            )
        )

    def _run_batch(self, checker):
        source_paths = sorted(
            path
            for path in self.source_path.iterdir()
            if path.is_file()
            and path.suffix.lower() in USD_EXTENSIONS
        )

        if not source_paths:
            self.results_output.setPlainText(
                "No supported USD files found in the selected directory."
            )
            return

        batch = BatchValidator(
            checker=checker
        ).validate(source_paths)

        lines = [
            "Batch Validation",
            "",
            f"Files: {batch.total_files}",
            f"Passed: {batch.passed_files}",
            f"Failed: {batch.failed_files}",
            "",
        ]

        lines.extend(
            f"[{'PASS' if report.publish_passed else 'FAIL'}] "
            f"{report.source_path}"
            for report in batch.reports
        )

        self.results_output.setPlainText("\n".join(lines))