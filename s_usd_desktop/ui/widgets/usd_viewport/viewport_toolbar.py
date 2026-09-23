from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QPushButton, QWidget


from s_usd_desktop.ui.tooltips import TooltipText


class ViewportToolbar(QWidget):
    source_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.source_edit = QLineEdit()
        self.source_edit.setPlaceholderText("Select a USD file to open or reload...")
        self.browse_button = QPushButton("Browse...")
        self.open_button = QPushButton("Open / Reload")
        self.source_edit.setToolTip(TooltipText.VIEWPORT_SOURCE)
        self.browse_button.setToolTip(TooltipText.VIEWPORT_BROWSE)
        self.open_button.setToolTip(TooltipText.VIEWPORT_LOAD)
        layout.addWidget(self.source_edit, 1)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.open_button)
        self.browse_button.clicked.connect(self._browse)
        self.open_button.clicked.connect(self._emit_source)
        self.source_edit.returnPressed.connect(self._emit_source)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select USD Stage", "", "USD Files (*.usd *.usda *.usdc *.usdz)")
        if path:
            self.source_edit.setText(path)
            self.source_requested.emit(path)

    def _emit_source(self):
        self.source_requested.emit(self.source_edit.text().strip())
