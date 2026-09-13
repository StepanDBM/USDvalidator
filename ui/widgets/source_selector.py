from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


USD_EXTENSIONS = {".usd", ".usda", ".usdc", ".usdz"}


class SourceSelector(QWidget):
    source_changed = Signal(object)

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

        self.browse_button = QPushButton("Browse...")
        self.browse_menu = QMenu(self)

        select_file_action = self.browse_menu.addAction("Select USD File...")
        select_folder_action = self.browse_menu.addAction("Select Folder...")

        select_file_action.triggered.connect(self._browse_file)
        select_folder_action.triggered.connect(self._browse_folder)

        self.browse_button.setMenu(self.browse_menu)

        source_layout.addWidget(self.source_label, 1)
        source_layout.addWidget(self.browse_button)

        layout.addLayout(source_layout)

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select USD File",
            self._initial_directory(),
            "USD Files (*.usd *.usda *.usdc *.usdz)",
        )

        if path:
            self.set_source(path)

    def _browse_folder(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "Select USD Folder",
            self._initial_directory(),
        )

        if path:
            self.set_source(path)

    def _initial_directory(self):
        if self.source_path is None:
            return ""

        if self.source_path.is_dir():
            return str(self.source_path)

        return str(self.source_path.parent)

    def set_source(self, path):
        source_path = Path(path).expanduser()

        if not source_path.exists():
            raise FileNotFoundError(
                f"Source does not exist: {source_path}"
            )

        if source_path.is_file():
            if source_path.suffix.lower() not in USD_EXTENSIONS:
                raise ValueError(
                    f"Unsupported USD extension: {source_path.suffix}"
                )

            source_type = "USD File"

        elif source_path.is_dir():
            source_type = "Folder"

        else:
            raise ValueError(
                f"Source must be a USD file or directory: {source_path}"
            )

        self.source_path = source_path

        self.source_label.setText(
            f"{source_type}: {source_path}"
        )

        self.source_label.setToolTip(
            str(source_path)
        )

        self.source_changed.emit(
            source_path
        )

    def get_source(self):
        return self.source_path

    def clear_source(self):
        self.source_path = None
        self.source_label.setText(
            "No file or folder selected"
        )
        self.source_label.setToolTip("")
        self.source_changed.emit(None)