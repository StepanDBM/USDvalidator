from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
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
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel("Source:"))

        self.source_label = QLabel("No file or folder selected")
        self.source_label.setMinimumWidth(300)

        self.browse_button = QPushButton("Browse")
        self.browse_button.setProperty("menuButton", True)

        self.browse_menu = QMenu(self)
        self.browse_button.setMenu(self.browse_menu)

        file_action = self.browse_menu.addAction("Select USD File...")
        folder_action = self.browse_menu.addAction("Select Folder...")
        file_action.triggered.connect(self._browse_file)

        folder_action.triggered.connect(self._browse_folder)
        self.browse_button.setMenu(self.browse_menu)
        layout.addWidget(self.source_label, 1)
        layout.addWidget(self.browse_button)

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select USD File",
            self._initial_directory()
        )

        if not path:
            return

        source_path = Path(path)

        if source_path.suffix.lower() not in USD_EXTENSIONS:
            return

        self.set_source(source_path)

    def _browse_folder(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select USD Folder",
            self._initial_directory()
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
            if (
                source_path.suffix.lower()
                not in USD_EXTENSIONS
            ):
                raise ValueError("The selected file is not a supported USD file.")

            source_type = "USD File"

        elif source_path.is_dir():
            source_type = "Folder"

        else:
            raise ValueError("The source must be a file or directory.")

        self.source_path = source_path
        self.source_label.setText(str(source_path))
        self.source_label.setToolTip(f"{source_type}: {source_path}")

        self.source_changed.emit(source_path)

    def get_source(self):
        return self.source_path

    def clear_source(self):
        self.source_path = None

        self.source_label.setText("No file or folder selected")

        self.source_label.setToolTip("")
        self.source_changed.emit(None)