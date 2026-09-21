from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout
)

from s_usd_desktop.services.desktop_settings import ConnectionPreferences


class ConnectionSettingsDialog(QDialog):
    def __init__(self, preferences, parent=None):
        super().__init__(parent)
        self.setWindowTitle("S-USDv Service Connection")
        self.setMinimumWidth(420)
        self.base_url = QLineEdit(preferences.base_url)
        self.connect_timeout = self._make_timeout(preferences.connect_timeout)
        self.request_timeout = self._make_timeout(preferences.request_timeout)
        self.auto_connect = QCheckBox("Connect automatically when S-USDv starts")
        self.auto_connect.setChecked(preferences.auto_connect)
        form = QFormLayout()
        form.addRow("Service URL", self.base_url)
        form.addRow("Connect timeout (seconds)", self.connect_timeout)
        form.addRow("Request timeout (seconds)", self.request_timeout)
        form.addRow("", self.auto_connect)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    @staticmethod
    def _make_timeout(value):
        control = QDoubleSpinBox()
        control.setRange(0.1, 600.0)
        control.setDecimals(1)
        control.setSingleStep(0.5)
        control.setValue(value)
        return control

    def preferences(self):
        return ConnectionPreferences(
            base_url=self.base_url.text(),
            connect_timeout=self.connect_timeout.value(),
            request_timeout=self.request_timeout.value(),
            auto_connect=self.auto_connect.isChecked()
        )

    def accept(self):
        try:
            self.preferences().to_api_configuration()
        except ValueError as error:
            self.base_url.setFocus()
            self.base_url.setToolTip(str(error))
            self.base_url.setStyleSheet("border: 1px solid #e53e3e;")
            return

        self.base_url.setStyleSheet("")
        super().accept()
