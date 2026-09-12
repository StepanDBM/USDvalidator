from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QTabBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from validation.profile_loader import ProfileLoader
from rules import build_registry

from .stylesheet import (
    dark_theme,
    light_theme,
    dark_blue_orange_theme,
)

from .widgets.validation_view import ValidationView
from .widgets.profile_editor import ProfileEditor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("USDvalidator")
        self.resize(1100, 700)

        self.profile_loader = ProfileLoader(
            "validation/profiles.json"
        )

        self.registry = build_registry()

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # --------------------------------------------------
        # Top bar
        # --------------------------------------------------

        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)

        top_layout.setContentsMargins(
            0, 0, 0, 0
        )

        # Custom tab bar
        self.tab_bar = QTabBar()

        self.tab_bar.addTab("Validation")
        self.tab_bar.addTab("Profiles")

        top_layout.addWidget(
            self.tab_bar
        )

        # Push theme controls to the right
        top_layout.addStretch()

        top_layout.addWidget(
            QLabel("Theme")
        )

        self.theme_selector = QComboBox()

        self.theme_selector.addItems(
            [
                "Dark",
                "Light",
                "Dark Blue / Orange",
            ]
        )

        top_layout.addWidget(
            self.theme_selector
        )

        main_layout.addWidget(
            top_bar
        )

        # --------------------------------------------------
        # Tab widget
        # --------------------------------------------------

        self.tabs = QTabWidget()

        # Hide the QTabWidget's own tab bar
        self.tabs.tabBar().hide()

        self.validation_view = ValidationView(
            profile_loader=self.profile_loader
        )

        self.profile_editor = ProfileEditor(
            profile_loader=self.profile_loader,
            registry=self.registry,
        )

        self.tabs.addTab(
            self.validation_view,
            "Validation",
        )

        self.tabs.addTab(
            self.profile_editor,
            "Profiles",
        )

        main_layout.addWidget(
            self.tabs,
            1,
        )

        self.setCentralWidget(
            central_widget
        )

    def _connect_signals(self):
        self.profile_editor.profiles_changed.connect(
            self._refresh_validation_profiles
        )

        self.tab_bar.currentChanged.connect(
            self.tabs.setCurrentIndex
        )

        self.tabs.currentChanged.connect(
            self.tab_bar.setCurrentIndex
        )

        self.theme_selector.currentIndexChanged.connect(
            self._change_theme
        )

    def _change_theme(self, index):
        themes = [
            dark_theme,
            light_theme,
            dark_blue_orange_theme,
        ]

        self.setStyleSheet(
            themes[index]()
        )

    def _refresh_validation_profiles(self):
        self.validation_view.refresh_profiles()