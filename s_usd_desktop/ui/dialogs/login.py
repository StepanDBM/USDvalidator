from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)


class LoginDialog(QDialog):
    def __init__(self, base_url, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sign in to S-USDv")
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)
        service = QLabel(f"Service: {base_url}")
        service.setWordWrap(True)
        layout.addWidget(service)
        form = QFormLayout()
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("artist@example.com")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Password")
        self.remember_check = QCheckBox("Keep me signed in on this computer")
        self.remember_check.setChecked(True)
        form.addRow("Email", self.email_edit)
        form.addRow("Password", self.password_edit)
        form.addRow("", self.remember_check)
        layout.addLayout(form)
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #e57373;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        layout.addWidget(self.error_label)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttons.button(QDialogButtonBox.Ok).setText("Sign in")
        self.buttons.accepted.connect(self._validate)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def credentials(self):
        return self.email_edit.text().strip(), self.password_edit.text(), self.remember_check.isChecked()

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()
        self.password_edit.selectAll()
        self.password_edit.setFocus()

    def _validate(self):
        email, password, _ = self.credentials()
        if not email or not password:
            self.show_error("Enter both email and password.")
            return
        self.accept()
