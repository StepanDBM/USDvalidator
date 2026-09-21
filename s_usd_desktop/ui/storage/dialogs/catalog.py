from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QPlainTextEdit,
    QVBoxLayout
)


class FormDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(420)
        self.form = QFormLayout()
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(self.form)
        layout.addWidget(buttons)

    def required_text(self, control, label):
        value = control.text().strip()

        if not value:
            control.setFocus()
            control.setToolTip(f"{label} is required")
            control.setStyleSheet("border: 1px solid #e53e3e;")
            return None

        control.setStyleSheet("")
        return value


class CreateProjectDialog(FormDialog):
    def __init__(self, parent=None):
        super().__init__("Create Project", parent)
        self.code = QLineEdit()
        self.name = QLineEdit()
        self.description = QPlainTextEdit()
        self.description.setMaximumHeight(90)
        self.form.addRow("Code", self.code)
        self.form.addRow("Name", self.name)
        self.form.addRow("Description", self.description)

    def values(self):
        code = self.required_text(self.code, "Code")
        name = self.required_text(self.name, "Name")
        return None if not code or not name else (code, name, self.description.toPlainText().strip())

    def accept(self):
        if self.values():
            super().accept()


class CreateAssetDialog(FormDialog):
    TYPES = ("character", "prop", "environment", "shot", "sequence", "other")

    def __init__(self, parent=None):
        super().__init__("Create Asset", parent)
        self.code = QLineEdit()
        self.name = QLineEdit()
        self.asset_type = QComboBox()
        self.asset_type.addItems(self.TYPES)
        self.description = QPlainTextEdit()
        self.description.setMaximumHeight(90)
        self.form.addRow("Code", self.code)
        self.form.addRow("Name", self.name)
        self.form.addRow("Type", self.asset_type)
        self.form.addRow("Description", self.description)

    def values(self):
        code = self.required_text(self.code, "Code")
        name = self.required_text(self.name, "Name")
        return None if not code or not name else (
            code,
            name,
            self.asset_type.currentText(),
            self.description.toPlainText().strip()
        )

    def accept(self):
        if self.values():
            super().accept()


class CreateStreamDialog(FormDialog):
    def __init__(self, parent=None):
        super().__init__("Create Stream", parent)
        self.name = QLineEdit()
        self.description = QPlainTextEdit()
        self.description.setMaximumHeight(90)
        self.form.addRow("Name", self.name)
        self.form.addRow("Description", self.description)

    def values(self):
        name = self.required_text(self.name, "Name")
        return None if not name else (name, self.description.toPlainText().strip())

    def accept(self):
        if self.values():
            super().accept()


class CreateVersionDialog(FormDialog):
    def __init__(self, parent=None):
        super().__init__("Create Version", parent)
        self.comment = QPlainTextEdit()
        self.comment.setMaximumHeight(110)
        self.form.addRow("Comment", self.comment)

    def values(self):
        return (self.comment.toPlainText().strip(),)
