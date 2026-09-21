from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from s_usd_desktop.services.connection_service import ConnectionState


class ConnectionIndicator(QWidget):
    reconnect_requested = Signal()
    settings_requested = Signal()

    COLORS = {
        ConnectionState.DISCONNECTED: "#8a8a8a",
        ConnectionState.CONNECTING: "#d69e2e",
        ConnectionState.CONNECTED: "#38a169",
        ConnectionState.ERROR: "#e53e3e"
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 0, 0)
        layout.setSpacing(6)
        self.dot = QLabel("●")
        self.label = QLabel("Disconnected")
        self.retry_button = QPushButton("Connect")
        self.settings_button = QPushButton("Service...")
        self.retry_button.clicked.connect(lambda: self.reconnect_requested.emit())
        self.settings_button.clicked.connect(lambda: self.settings_requested.emit())
        layout.addWidget(self.dot)
        layout.addWidget(self.label)
        layout.addWidget(self.retry_button)
        layout.addWidget(self.settings_button)
        self.set_state(ConnectionState.DISCONNECTED)

    def set_state(self, state, health=None, error=""):
        self.dot.setStyleSheet(f"color: {self.COLORS[state]};")

        if state == ConnectionState.CONNECTED and health:
            text = f"Connected: {health.service} {health.version}"
        elif state == ConnectionState.CONNECTING:
            text = "Connecting..."
        elif state == ConnectionState.ERROR:
            text = "Connection error"
        else:
            text = "Disconnected"

        self.label.setText(text)
        self.label.setToolTip(error)
        self.retry_button.setText("Retry" if state == ConnectionState.ERROR else "Connect")
        self.retry_button.setVisible(state in {ConnectionState.DISCONNECTED, ConnectionState.ERROR})
        self.settings_button.setEnabled(state != ConnectionState.CONNECTING)
