from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton


class ValidateButton(QPushButton):
    validate_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("Run Validation", parent)

        self.clicked.connect(self.validate_requested.emit)