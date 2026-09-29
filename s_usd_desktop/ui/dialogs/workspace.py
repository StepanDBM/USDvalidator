from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)


class CreateWorkspaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Workspace")
        self.setMinimumWidth(460)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.code_edit = QLineEdit()
        self.code_edit.setMaxLength(64)
        self.code_edit.setPlaceholderText("Workspace CODE")
        self.code_edit.setToolTip("Enter a short unique workspace code. The service normalizes the code to uppercase.")
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(128)
        self.name_edit.setPlaceholderText("OpenUSD Workspace")
        self.name_edit.setToolTip("Enter the descriptive workspace name shown throughout the desktop application.")
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setPlaceholderText("Optional workspace purpose or production description")
        self.description_edit.setToolTip(
            "Describe the workspace purpose. This field is optional and can contain up to 2,000 characters."
        )
        form.addRow("Code", self.code_edit)
        form.addRow("Name", self.name_edit)
        form.addRow("Description", self.description_edit)
        layout.addLayout(form)
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #e57373;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        layout.addWidget(self.error_label)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttons.button(QDialogButtonBox.Ok).setText("Create")
        self.buttons.accepted.connect(self._validate)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def workspace_data(self):
        return {
            "code": self.code_edit.text().strip(),
            "name": self.name_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
        }

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()

    def _validate(self):
        data = self.workspace_data()
        if not data["code"] or not data["name"]:
            self.show_error("Code and name are required.")
            return
        self.accept()


class ManageWorkspaceDialog(QDialog):
    ROLES = ("viewer", "contributor", "administrator", "owner")

    def __init__(self, workspace, session_service, parent=None):
        super().__init__(parent)
        self.workspace = workspace
        self.session_service = session_service
        self.setWindowTitle(f"Manage Workspace · {workspace.code}")
        self.resize(720, 460)
        layout = QVBoxLayout(self)
        heading = QLabel(f"<b>{workspace.code}</b> · {workspace.name}")
        heading.setTextFormat(Qt.RichText)
        layout.addWidget(heading)
        if workspace.description:
            description = QLabel(workspace.description)
            description.setWordWrap(True)
            layout.addWidget(description)
        self.member_table = QTableWidget(0, 3)
        self.member_table.setHorizontalHeaderLabels(("Email", "Display name", "Role"))
        self.member_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.member_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.member_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.member_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.member_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.member_table.setToolTip("Lists users who can access this workspace and each user's assigned role.")
        layout.addWidget(self.member_table)
        add_layout = QHBoxLayout()
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("existing-user@example.com")
        self.email_edit.setToolTip("Enter the email address of an existing active S-USDv user.")
        self.role_combo = QComboBox()
        self.role_combo.addItems(self.ROLES)
        self.role_combo.setCurrentText("contributor")
        self.role_combo.setToolTip("Choose the workspace permissions assigned to the existing user.")
        self.add_button = QPushButton("Add member")
        self.add_button.setToolTip("Add the existing active user to this workspace with the selected role.")
        self.add_button.clicked.connect(self._add_member)
        add_layout.addWidget(self.email_edit, 1)
        add_layout.addWidget(self.role_combo)
        add_layout.addWidget(self.add_button)
        layout.addLayout(add_layout)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.refresh_members()

    def refresh_members(self):
        try:
            members = self.session_service.list_members(self.workspace.id)
        except Exception as error:
            QMessageBox.warning(self, "Workspace members", str(error))
            return
        self.member_table.setRowCount(len(members))
        for row, member in enumerate(members):
            self.member_table.setItem(row, 0, QTableWidgetItem(member["user"]["email"]))
            self.member_table.setItem(row, 1, QTableWidgetItem(member["user"]["display_name"]))
            self.member_table.setItem(row, 2, QTableWidgetItem(member["role"]))

    def _add_member(self):
        email = self.email_edit.text().strip()
        if not email:
            QMessageBox.warning(self, "Add member", "Enter an existing user's email address.")
            return
        try:
            self.session_service.add_member(self.workspace.id, email, self.role_combo.currentText())
        except Exception as error:
            QMessageBox.warning(self, "Add member", str(error))
            return
        self.email_edit.clear()
        self.refresh_members()
