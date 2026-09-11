from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


USD_EXTENSIONS = {".usd", ".usda", ".usdc", ".usdz"}


class SourceSelector(QWidget):
    source_changed = Signal(object)
    mode_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.source_path = None

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Source"))

        source_layout = QHBoxLayout()

        self.source_label = QLabel("No file or folder selected")
        self.source_label.setWordWrap(True)

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse)

        source_layout.addWidget(self.source_label, 1)
        source_layout.addWidget(browse_button)

        layout.addLayout(source_layout)

        mode_layout = QHBoxLayout()

        mode_layout.addWidget(QLabel("Mode:"))

        self.file_radio = QRadioButton("File")
        self.folder_radio = QRadioButton("Folder")

        self.file_radio.setChecked(True)

        self.file_radio.toggled.connect(self._on_mode_changed)
        self.folder_radio.toggled.connect(self._on_mode_changed)

        mode_layout.addWidget(self.file_radio)
        mode_layout.addWidget(self.folder_radio)
        mode_layout.addStretch()

        layout.addLayout(mode_layout)

    def _browse(self):
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

        self.set_source(Path(path))

    def _on_mode_changed(self):
        self.source_path = None
        self.source_label.setText("No file or folder selected")

        mode = "file" if self.file_radio.isChecked() else "folder"
        self.mode_changed.emit(mode)

    def set_source(self, path):
        self.source_path = Path(path)
        self.source_label.setText(str(self.source_path))
        self.source_changed.emit(self.source_path)

    def get_source(self):
        return self.source_path

    def is_file_mode(self):
        return self.file_radio.isChecked()

    def is_folder_mode(self):
        return self.folder_radio.isChecked()