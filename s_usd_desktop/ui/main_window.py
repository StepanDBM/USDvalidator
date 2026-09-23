from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QDialog,
    QTabBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from s_usd_core.validation.profile_loader import ProfileLoader
from s_usd_core.rules import build_registry
from s_usd_desktop.services import ConnectionService
from s_usd_desktop.ui.tooltips import TooltipText

from .stylesheet import (
    dark_theme,
    light_theme,
    dark_blue_orange_theme,
)

from .widgets.validation_view import ValidationView
from .widgets.profile_editor import ProfileEditor
from .widgets.comparison_browser import ComparisonView
from .widgets.usd_viewport import create_usd_viewport
from .widgets.connection import ConnectionIndicator
from .dialogs.connection_settings import ConnectionSettingsDialog

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
        for index, text in enumerate((
            TooltipText.TAB_VALIDATION,
            TooltipText.TAB_PROFILES,
            TooltipText.TAB_COMPARISON,
            TooltipText.TAB_VIEWPORT
        )):
            self.tab_bar.setTabToolTip(index, text)

        top_layout.addWidget(self.tab_bar)

        # Push theme controls to the right
        top_layout.addStretch()
        self.connection_indicator = ConnectionIndicator()
        self.connection_indicator.setToolTip(TooltipText.SERVICE_INDICATOR)
        top_layout.addWidget(self.connection_indicator)
        top_layout.addSpacing(10)
        top_layout.addWidget(QLabel("Theme"))
        self.theme_selector = QComboBox()
        self.theme_selector.setToolTip(TooltipText.THEME_SELECTOR)
        self.theme_selector.addItems(
            [
                "Dark Blue / Orange",
                "Dark",
                "Light"
            ]
        )

        top_layout.addWidget(self.theme_selector)
        main_layout.addWidget(top_bar)

        # --------------------------------------------------
        # Tab widget
        # --------------------------------------------------

        self.tabs = QTabWidget()

        # Hide the QTabWidget's own tab bar
        self.tabs.tabBar().hide()
        self.validation_view = ValidationView(profile_loader=self.profile_loader)
        self.profile_editor = ProfileEditor(profile_loader=self.profile_loader,
            registry=self.registry,)

        self.comparison_view = ComparisonView(profile_loader=self.profile_loader)
        self.viewport_view = create_usd_viewport()
        self.tabs.addTab(self.validation_view, "Validation")
        self.tabs.addTab(self.profile_editor, "Profiles")
        self.tabs.addTab(self.comparison_view, "Comparison")
        self.tabs.addTab(self.viewport_view, "Viewport")
        for index, text in enumerate((
            TooltipText.TAB_VALIDATION,
            TooltipText.TAB_PROFILES,
            TooltipText.TAB_COMPARISON,
            TooltipText.TAB_VIEWPORT
        )):
            self.tabs.setTabToolTip(index, text)
        main_layout.addWidget(self.tabs, 1)
        self.setCentralWidget(central_widget)

    def _connect_signals(self):
        self.profile_editor.profiles_changed.connect(self._refresh_validation_profiles)
        self.tab_bar.currentChanged.connect(self.tabs.setCurrentIndex)
        self.tabs.currentChanged.connect(self.tab_bar.setCurrentIndex)
        self.theme_selector.currentIndexChanged.connect(self._change_theme)
        self.validation_view.open_in_viewport_requested.connect(self._open_validation_result_in_viewport)
        self.comparison_view.open_in_viewport_requested.connect(self._open_comparison_change_in_viewport)
        self.viewport_view.validation_requested.connect(self._validate_viewport_source)
        self.validation_view.report_ready.connect(self._handle_validation_report)
        self.validation_view.validation_finished.connect(self.viewport_view.retry_pending_validation)
        self.connection_indicator.reconnect_requested.connect(
            self.connection_service.connect_to_service
        )
        self.connection_indicator.settings_requested.connect(
            self._show_connection_settings
        )
        self.connection_service.state_changed.connect(
            self._update_connection_indicator
        )
        self.connection_service.connected.connect(
            lambda health: self._update_connection_indicator(
                self.connection_service.state,
                health
            )
        )
        self.connection_service.connection_failed.connect(
            lambda error: self._update_connection_indicator(
                self.connection_service.state,
                error=error
            )
        )

    def _update_connection_indicator(self, state, health=None, error=""):
        self.connection_indicator.set_state(
            state,
            health or self.connection_service.health,
            error or self.connection_service.last_error
        )

    def _show_connection_settings(self):
        dialog = ConnectionSettingsDialog(
            self.connection_service.preferences,
            self
        )

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
        themes = [
            dark_blue_orange_theme,
            dark_theme,
            light_theme
        ]

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