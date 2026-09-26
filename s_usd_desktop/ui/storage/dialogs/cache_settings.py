from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget
)

from s_usd_desktop.cache import CacheConfiguration, default_cache_root


class CacheSettings:
    def __init__(self, settings=None):
        self.settings = settings or QSettings("Styopa", "S-USDv")

    def configuration(self):
        return CacheConfiguration(
            root=Path(self.settings.value("cache/root", str(default_cache_root()), str)),
            maximum_bytes=self.settings.value("cache/maximum_gib", 50, int) * 1024**3,
            verify_on_access=self.settings.value("cache/verify_on_access", True, bool)
        )

    def save(self, configuration):
        self.settings.setValue("cache/root", str(configuration.root))
        self.settings.setValue("cache/maximum_gib", configuration.maximum_bytes // 1024**3)
        self.settings.setValue("cache/verify_on_access", configuration.verify_on_access)
        self.settings.sync()


from s_usd_desktop.ui.tooltips import TooltipText


class CacheSettingsDialog(QDialog):
    def __init__(self, configuration, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Managed Cache Settings")
        self.setMinimumWidth(540)
        self.root = QLineEdit(str(configuration.root))
        browse = QPushButton("Browse...")
        self.root.setToolTip(TooltipText.CACHE_ROOT)
        browse.setToolTip(TooltipText.CACHE_ROOT)
        browse.clicked.connect(self._browse)
        root_widget = QWidget()
        root_layout = QHBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self.root, 1)
        root_layout.addWidget(browse)
        self.maximum_gib = QSpinBox()
        self.maximum_gib.setRange(1, 4096)
        self.maximum_gib.setValue(max(1, configuration.maximum_bytes // 1024**3))
        self.verify = QCheckBox("Verify SHA-256 when cached files are inspected")
        self.maximum_gib.setToolTip(TooltipText.CACHE_LIMIT)
        self.verify.setToolTip(TooltipText.CACHE_VERIFY_ON_ACCESS)
        self.verify.setChecked(configuration.verify_on_access)
        form = QFormLayout()
        form.addRow("Cache location", root_widget)
        form.addRow("Maximum size (GiB)", self.maximum_gib)
        form.addRow("", self.verify)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _browse(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Cache Location", self.root.text())
        if directory:
            self.root.setText(directory)

    def configuration(self):
        return CacheConfiguration(
            root=Path(self.root.text().strip()),
            maximum_bytes=self.maximum_gib.value() * 1024**3,
            verify_on_access=self.verify.isChecked()
        )

    def accept(self):
        if not self.root.text().strip():
            self.root.setFocus()
            self.root.setStyleSheet("border: 1px solid #e53e3e;")
            return
        super().accept()
