from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from s_usd_core.rules import build_registry
from s_usd_core.validation.profile_loader import ProfileLoader
from s_usd_desktop.services import ConnectionService
from s_usd_desktop.services.session_service import SessionService, SessionState
from s_usd_desktop.ui.tooltips import TooltipText

from .dialogs.connection_settings import ConnectionSettingsDialog
from .dialogs.login import LoginDialog
from .dialogs.workspace import CreateWorkspaceDialog, ManageWorkspaceDialog
from .stylesheet import (
    dark_blue_orange_theme,
    dark_theme,
    light_theme,
)
from .widgets.comparison_browser import ComparisonView
from .widgets.connection import ConnectionIndicator
from .widgets.profile_editor import ProfileEditor
from .widgets.usd_viewport import create_usd_viewport
from .widgets.validation_view import ValidationView


def _change_theme(self, index):
    themes = (
        dark_theme,
        light_theme,
        dark_blue_orange_theme,
    )

    application = QApplication.instance()

    if application is not None:
        application.setStyleSheet(themes)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("S-USDv")
        self.resize(1280, 800)

        self.profile_loader = ProfileLoader("s_usd_core/validation/profiles.json")

        self.registry = build_registry()
        self.connection_service = ConnectionService(parent=self)
        self.session_service = SessionService(self.connection_service, parent=self)

        self._build_ui()
        self._connect_signals()
        self._change_theme(self.theme_selector.currentIndex())

        if self.connection_service.preferences.auto_connect:
            self.connection_service.connect_to_service()

    def _build_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # --------------------------------------------------
        # Top bar
        # --------------------------------------------------

        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)

        top_layout.setContentsMargins(0, 0, 0, 0)

        # Custom tab bar
        self.tab_bar = QTabBar()
        self.tab_bar.setToolTip(
            "Switch between validation, profile editing, comparison, viewport, "
            "and shared storage workspaces. Switching tabs does not cancel work."
        )

        self.tab_bar.addTab("Validation")
        self.tab_bar.addTab("Profiles")
        self.tab_bar.addTab("Comparison")
        self.tab_bar.addTab("Viewport")
        for index, text in enumerate(
            (TooltipText.TAB_VALIDATION, TooltipText.TAB_PROFILES, TooltipText.TAB_COMPARISON, TooltipText.TAB_VIEWPORT)
        ):
            self.tab_bar.setTabToolTip(index, text)

        top_layout.addWidget(self.tab_bar)

        # Push theme controls to the right
        top_layout.addStretch()
        self.connection_indicator = ConnectionIndicator()
        self.connection_indicator.setToolTip(TooltipText.SERVICE_INDICATOR)
        top_layout.addWidget(self.connection_indicator)
        self.workspace_selector = QComboBox()
        self.workspace_selector.setMinimumWidth(170)
        self.workspace_selector.setPlaceholderText("No workspace")
        self.workspace_selector.setEnabled(False)
        top_layout.addWidget(self.workspace_selector)
        self.create_workspace_button = QPushButton("+")
        self.create_workspace_button.setFixedWidth(30)
        self.create_workspace_button.setToolTip(
            "Create a new workspace. The signed-in user automatically becomes the workspace Owner."
        )
        self.create_workspace_button.setEnabled(False)
        top_layout.addWidget(self.create_workspace_button)
        self.manage_workspace_button = QPushButton("Manage")
        self.manage_workspace_button.setToolTip(
            "View the selected workspace and add existing active users as workspace members."
        )
        self.manage_workspace_button.setEnabled(False)
        top_layout.addWidget(self.manage_workspace_button)
        self.session_button = QPushButton("Sign in")
        top_layout.addWidget(self.session_button)
        top_layout.addSpacing(10)
        top_layout.addWidget(QLabel("Theme"))
        self.theme_selector = QComboBox()
        self.theme_selector.setToolTip(TooltipText.THEME_SELECTOR)
        self.theme_selector.addItems(["Dark Blue / Orange", "Dark", "Light"])

        top_layout.addWidget(self.theme_selector)
        main_layout.addWidget(top_bar)

        # --------------------------------------------------
        # Tab widget
        # --------------------------------------------------

        self.tabs = QTabWidget()

        # Hide the QTabWidget's own tab bar
        self.tabs.tabBar().hide()
        self.validation_view = ValidationView(profile_loader=self.profile_loader)
        self.profile_editor = ProfileEditor(
            profile_loader=self.profile_loader,
            registry=self.registry,
        )

        self.comparison_view = ComparisonView(profile_loader=self.profile_loader)
        self.viewport_view = create_usd_viewport()
        self.tabs.addTab(self.validation_view, "Validation")
        self.tabs.addTab(self.profile_editor, "Profiles")
        self.tabs.addTab(self.comparison_view, "Comparison")
        self.tabs.addTab(self.viewport_view, "Viewport")
        for index, text in enumerate(
            (TooltipText.TAB_VALIDATION, TooltipText.TAB_PROFILES, TooltipText.TAB_COMPARISON, TooltipText.TAB_VIEWPORT)
        ):
            self.tabs.setTabToolTip(index, text)
        main_layout.addWidget(self.tabs, 1)
        self.setCentralWidget(central_widget)

    def _connect_signals(self):
        self.session_button.clicked.connect(self._toggle_session)
        self.create_workspace_button.clicked.connect(self._create_workspace)
        self.manage_workspace_button.clicked.connect(self._manage_workspace)
        self.workspace_selector.currentIndexChanged.connect(self._workspace_selected)
        self.session_service.state_changed.connect(self._session_state_changed)
        self.session_service.workspaces_changed.connect(self._set_workspaces)
        self.session_service.authentication_failed.connect(self._show_authentication_failure)
        self.connection_service.connected.connect(lambda _health: self.session_service.restore())
        self.profile_editor.profiles_changed.connect(self._refresh_validation_profiles)
        self.tab_bar.currentChanged.connect(self.tabs.setCurrentIndex)
        self.tabs.currentChanged.connect(self.tab_bar.setCurrentIndex)
        self.theme_selector.currentIndexChanged.connect(self._change_theme)
        self.validation_view.open_in_viewport_requested.connect(self._open_validation_result_in_viewport)
        self.comparison_view.open_in_viewport_requested.connect(self._open_comparison_change_in_viewport)
        self.viewport_view.validation_requested.connect(self._validate_viewport_source)
        self.validation_view.report_ready.connect(self._handle_validation_report)
        self.validation_view.validation_finished.connect(self.viewport_view.retry_pending_validation)
        self.connection_indicator.reconnect_requested.connect(self.connection_service.connect_to_service)
        self.connection_indicator.settings_requested.connect(self._show_connection_settings)
        self.connection_service.state_changed.connect(self._update_connection_indicator)
        self.connection_service.connected.connect(
            lambda health: self._update_connection_indicator(self.connection_service.state, health)
        )
        self.connection_service.connection_failed.connect(
            lambda error: self._update_connection_indicator(self.connection_service.state, error=error)
        )

    def _update_connection_indicator(self, state, health=None, error=""):
        self.connection_indicator.set_state(
            state, health or self.connection_service.health, error or self.connection_service.last_error
        )

    def _toggle_session(self):
        if self.session_service.state == SessionState.AUTHENTICATED:
            self.session_service.sign_out()
            return

        dialog = LoginDialog(self.connection_service.preferences.base_url, self)
        if dialog.exec() != QDialog.Accepted:
            return

        email, password, remember = dialog.credentials()
        if not self.session_service.sign_in(email, password, remember):
            self._show_authentication_failure(self.session_service.last_error)

    def _session_state_changed(self, state):
        authenticated = state == SessionState.AUTHENTICATED
        self.session_button.setText("Sign out" if authenticated else "Sign in")
        self.session_button.setEnabled(state != SessionState.AUTHENTICATING)
        self.workspace_selector.setEnabled(authenticated and self.workspace_selector.count() > 0)
        self.create_workspace_button.setEnabled(authenticated)
        self.manage_workspace_button.setEnabled(authenticated and self.workspace_selector.count() > 0)

    def _set_workspaces(self, workspaces):
        selected_id = self.connection_service.settings.current_workspace_id()
        self.workspace_selector.blockSignals(True)
        self.workspace_selector.clear()

        for workspace in workspaces:
            self.workspace_selector.addItem(f"{workspace.code} · {workspace.name}", workspace.id)

        selected_index = self.workspace_selector.findData(selected_id)
        fallback_index = 0 if workspaces else -1
        self.workspace_selector.setCurrentIndex(selected_index if selected_index >= 0 else fallback_index)
        self.workspace_selector.blockSignals(False)
        authenticated = self.session_service.state == SessionState.AUTHENTICATED
        self.workspace_selector.setEnabled(authenticated and bool(workspaces))
        self.manage_workspace_button.setEnabled(authenticated and bool(workspaces))

        if workspaces:
            self._workspace_selected(self.workspace_selector.currentIndex())

    def _create_workspace(self):
        dialog = CreateWorkspaceDialog(self)
        while dialog.exec() == QDialog.Accepted:
            data = dialog.workspace_data()
            try:
                workspace = self.session_service.create_workspace(**data)
            except Exception as error:
                dialog.show_error(getattr(error, "message", str(error)))
                continue
            QMessageBox.information(
                self,
                "Workspace created",
                f"Workspace {workspace.code} was created. You are its Owner.",
            )
            break

    def _manage_workspace(self):
        workspace = self.session_service.current_workspace
        if workspace is None:
            QMessageBox.information(self, "Manage Workspace", "Select a workspace first.")
            return
        ManageWorkspaceDialog(workspace, self.session_service, self).exec()

    def _workspace_selected(self, index):
        if index >= 0:
            self.session_service.select_workspace(self.workspace_selector.itemData(index))

    def _show_authentication_failure(self, message):
        if self.isVisible():
            QMessageBox.warning(self, "S-USDv authentication", message)

    def _show_connection_settings(self):
        dialog = ConnectionSettingsDialog(self.connection_service.preferences, self)

        if dialog.exec() == QDialog.Accepted:
            self.connection_service.apply_preferences(dialog.preferences())

    def _open_validation_result_in_viewport(self, report, result):
        index = self.tabs.indexOf(self.viewport_view)
        self.tabs.setCurrentIndex(index)
        self.tab_bar.setCurrentIndex(index)
        self.viewport_view.show_validation_result(report, result)

    def _open_comparison_change_in_viewport(self, comparison, change, side):
        index = self.tabs.indexOf(self.viewport_view)
        self.tabs.setCurrentIndex(index)
        self.tab_bar.setCurrentIndex(index)
        self.viewport_view.show_comparison_change(comparison, change, side)

    def _change_theme(self, index):
        themes = [dark_blue_orange_theme, dark_theme, light_theme]

        self.setStyleSheet(themes[index]())

    def closeEvent(self, event):
        self.viewport_view.shutdown()
        super().closeEvent(event)

    def _refresh_validation_profiles(self):
        self.validation_view.refresh_profiles()

    def _validate_viewport_source(
        self,
        source_path,
        force=False,
    ):
        started = self.validation_view.validate_source(source_path, viewport_request=True)
        if not started:
            self.viewport_view.defer_validation(source_path, force)

    def _handle_validation_report(self, report):
        self.viewport_view.set_validation_report(report)
