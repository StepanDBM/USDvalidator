from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget
)


from s_usd_desktop.ui.tooltips import TooltipText


class UploadFileDialog(QDialog):
    ROLES = ("root_layer", "dependency", "texture", "preview", "manifest", "report", "other")

    def __init__(self, parent=None, initial_role=None):
        super().__init__(parent)
        self.setWindowTitle("Upload File")
        self.setMinimumWidth(520)
        self.path = QLineEdit()
        browse = QPushButton("Browse...")
        self.path.setToolTip(TooltipText.UPLOAD_LOCAL_FILE)
        browse.setToolTip(TooltipText.UPLOAD_LOCAL_FILE)
        browse.clicked.connect(self._browse)
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(self.path, 1)
        row_layout.addWidget(browse)
        self.role = QComboBox()
        self.role.addItems(self.ROLES)
        if initial_role in self.ROLES:
            self.role.setCurrentText(initial_role)
        self.relative_path = QLineEdit()
        self.role.setToolTip(TooltipText.UPLOAD_ROLE)
        self.relative_path.setToolTip(TooltipText.UPLOAD_RELATIVE_PATH)
        form = QFormLayout()
        form.addRow("Local file", row)
        form.addRow("Role", self.role)
        form.addRow("Relative package path", self.relative_path)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _browse(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select OpenUSD File",
            "",
            "OpenUSD (*.usd *.usda *.usdc *.usdz)"
        )

        if filename:
            self.path.setText(filename)
            self.relative_path.setText(Path(filename).name)

    def values(self):
        source = Path(self.path.text().strip())
        relative_path = self.relative_path.text().strip()

        if not source.is_file():
            self.path.setFocus()
            self.path.setStyleSheet("border: 1px solid #e53e3e;")
            return None

        if not relative_path:
            self.relative_path.setFocus()
            self.relative_path.setStyleSheet("border: 1px solid #e53e3e;")
            return None

        self.path.setStyleSheet("")
        self.relative_path.setStyleSheet("")
        return source, self.role.currentText(), relative_path

    def accept(self):
        if self.values():
            super().accept()
