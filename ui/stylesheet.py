from dataclasses import dataclass


@dataclass(frozen=True)
class ThemePalette:
    window: str
    surface: str
    surface_hover: str
    surface_pressed: str
    panel: str
    input: str
    text: str
    text_muted: str
    border: str
    border_disabled: str
    accent: str
    accent_hover: str
    accent_soft: str
    accent_pressed: str
    accent_text: str
    selection: str
    selection_text: str
    disabled: str
    disabled_text: str
    tooltip: str


DARK_PALETTE = ThemePalette(
    window="#171717",
    surface="#292a2d",
    surface_hover="#3b3218",
    surface_pressed="#211c0e",
    panel="#202124",
    input="#303134",
    text="#e8eaed",
    text_muted="#9aa0a6",
    border="#5f6368",
    border_disabled="#3c4043",
    accent="#e0b72f",
    accent_hover="#f5d76e",
    accent_soft="#3b3218",
    accent_pressed="#b8921f",
    accent_text="#111111",
    selection="#c9a227",
    selection_text="#111111",
    disabled="#292a2d",
    disabled_text="#80868b",
    tooltip="#303134",
)


LIGHT_PALETTE = ThemePalette(
    window="#f4f6f8",
    surface="#ffffff",
    surface_hover="#edf7f1",
    surface_pressed="#d7f0e1",
    panel="#ffffff",
    input="#ffffff",
    text="#202124",
    text_muted="#6b7280",
    border="#b8bec6",
    border_disabled="#d4d8dd",
    accent="#198754",
    accent_hover="#146c43",
    accent_soft="#edf7f1",
    accent_pressed="#0f5132",
    accent_text="#ffffff",
    selection="#198754",
    selection_text="#ffffff",
    disabled="#e6e9ed",
    disabled_text="#9aa0a6",
    tooltip="#ffffff",
)


DARK_BLUE_ORANGE_PALETTE = ThemePalette(
    window="#081321",
    surface="#12243d",
    surface_hover="#1a3152",
    surface_pressed="#09111f",
    panel="#0b1628",
    input="#101f35",
    text="#f4f1ea",
    text_muted="#b9c5d4",
    border="#38506d",
    border_disabled="#34445a",
    accent="#e58a3a",
    accent_hover="#f0a35d",
    accent_soft="#243d5d",
    accent_pressed="#c96f2d",
    accent_text="#ffffff",
    selection="#c96f2d",
    selection_text="#ffffff",
    disabled="#101c2e",
    disabled_text="#66758a",
    tooltip="#12243d",
)


def build_theme(palette):
    return f"""
QMainWindow,
QDialog {{
    background: {palette.window};
}}

QWidget {{
    color: {palette.text};
    font-size: 13px;
    background: {palette.window};
}}

QFrame {{
    border-color: {palette.border};
}}

/* Buttons */

QPushButton {{
    min-height: 20px;
    padding: 5px 12px;
    border: 1px solid {palette.border};
    border-radius: 5px;
    background: {palette.surface};
    color: {palette.text};
}}

QPushButton:hover {{
    border-color: {palette.accent};
    background: {palette.surface_hover};
    color: {palette.accent_hover};
}}

QPushButton:focus {{
    border-color: {palette.accent};
}}

QPushButton:pressed {{
    border-color: {palette.accent_pressed};
    background: {palette.surface_pressed};
    color: {palette.accent};
}}

QPushButton:checked {{
    border-color: {palette.accent};
    background: {palette.accent_soft};
    color: {palette.accent_hover};
}}

QPushButton:disabled {{
    border-color: {palette.border_disabled};
    background: {palette.disabled};
    color: {palette.disabled_text};
}}

QPushButton[menuButton="true"] {{
    padding-right: 26px;
}}

QPushButton[menuButton="true"]::menu-indicator {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    right: 8px;
}}

/* Tool buttons */

QToolButton {{
    min-height: 20px;
    padding: 5px 8px;
    border: 1px solid transparent;
    border-radius: 5px;
    background: transparent;
    color: {palette.text};
}}

QToolButton:hover {{
    border-color: {palette.accent};
    background: {palette.accent_soft};
    color: {palette.accent_hover};
}}

QToolButton:checked {{
    border-color: {palette.accent};
    background: {palette.accent_soft};
    color: {palette.accent_hover};
}}

/* Text and numeric inputs */

QLineEdit,
QSpinBox,
QDoubleSpinBox {{
    min-height: 20px;
    padding: 5px 8px;
    border: 1px solid {palette.border};
    border-radius: 5px;
    background: {palette.input};
    color: {palette.text};
    selection-background-color: {palette.selection};
    selection-color: {palette.selection_text};
}}

QLineEdit:hover,
QLineEdit:focus,
QSpinBox:hover,
QSpinBox:focus,
QDoubleSpinBox:hover,
QDoubleSpinBox:focus {{
    border-color: {palette.accent};
}}

QLineEdit:disabled,
QSpinBox:disabled,
QDoubleSpinBox:disabled {{
    border-color: {palette.border_disabled};
    background: {palette.disabled};
    color: {palette.disabled_text};
}}

/* Combo boxes */

QComboBox {{
    min-height: 20px;
    padding: 5px 8px;
    border: 1px solid {palette.border};
    border-radius: 5px;
    background: {palette.input};
    color: {palette.text};
    selection-background-color: {palette.selection};
    selection-color: {palette.selection_text};
}}

QComboBox:hover,
QComboBox:focus,
QComboBox:on {{
    border-color: {palette.accent};
}}

QComboBox:disabled {{
    border-color: {palette.border_disabled};
    background: {palette.disabled};
    color: {palette.disabled_text};
}}


QComboBox QAbstractItemView {{
    padding: 4px;
    border: 1px solid {palette.accent};
    border-radius: 5px;
    outline: none;
    background: {palette.input};
    color: {palette.text};
    selection-background-color: {palette.selection};
    selection-color: {palette.selection_text};
}}

QComboBox QAbstractItemView::item {{
    min-height: 22px;
    padding: 4px 8px;
}}

/* Spin-box controls */

QSpinBox::up-button,
QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 22px;
    border: none;
    border-left: 1px solid {palette.border};
    border-top-right-radius: 5px;
    background: {palette.surface};
}}

QSpinBox::down-button,
QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 22px;
    border: none;
    border-left: 1px solid {palette.border};
    border-bottom-right-radius: 5px;
    background: {palette.surface};
}}

QSpinBox::up-button:hover,
QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover,
QDoubleSpinBox::down-button:hover {{
    background: {palette.accent_soft};
}}

/* Check boxes */

QCheckBox {{
    spacing: 7px;
    background: transparent;
}}

QCheckBox::indicator {{
    width: 15px;
    height: 15px;
    border: 1px solid {palette.border};
    border-radius: 3px;
    background: {palette.input};
}}

QCheckBox::indicator:hover {{
    border-color: {palette.accent};
}}

QCheckBox::indicator:checked {{
    border-color: {palette.accent};
    background: {palette.accent};
}}

QCheckBox::indicator:disabled {{
    border-color: {palette.border_disabled};
    background: {palette.disabled};
}}

/* Views */

QTextEdit,
QTextBrowser,
QPlainTextEdit,
QListView,
QListWidget,
QTreeView,
QTreeWidget,
QTableView,
QTableWidget {{
    border: 1px solid {palette.border};
    border-radius: 5px;
    background: {palette.panel};
    color: {palette.text};
    selection-background-color: {palette.selection};
    selection-color: {palette.selection_text};
    alternate-background-color: {palette.surface};
}}

QListView::item,
QListWidget::item,
QTreeView::item,
QTreeWidget::item,
QTableView::item,
QTableWidget::item {{
    min-height: 20px;
    padding: 3px 5px;
}}

QListView::item:hover,
QListWidget::item:hover,
QTreeView::item:hover,
QTreeWidget::item:hover,
QTableView::item:hover,
QTableWidget::item:hover {{
    background: {palette.accent_soft};
}}

QListView::item:selected,
QListWidget::item:selected,
QTreeView::item:selected,
QTreeWidget::item:selected,
QTableView::item:selected,
QTableWidget::item:selected {{
    background: {palette.selection};
    color: {palette.selection_text};
}}

/* Headers */

QHeaderView {{
    background: {palette.surface};
}}

QHeaderView::section {{
    padding: 5px 8px;
    border: none;
    border-right: 1px solid {palette.border};
    border-bottom: 2px solid {palette.accent};
    background: {palette.surface};
    color: {palette.accent_hover};
}}

QTableCornerButton::section {{
    border: none;
    border-right: 1px solid {palette.border};
    border-bottom: 2px solid {palette.accent};
    background: {palette.surface};
}}

/* Group boxes */

QGroupBox {{
    margin-top: 10px;
    padding: 12px 8px 8px 8px;
    border: 1px solid {palette.border};
    border-radius: 5px;
    background: {palette.window};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    background: {palette.window};
    color: {palette.accent_hover};
}}

/* Tabs */

QTabWidget::pane {{
    border: 1px solid {palette.border};
    border-radius: 5px;
    background: {palette.window};
}}

QTabBar::tab {{
    min-width: 76px;
    padding: 7px 14px;
    border: 1px solid {palette.border};
    border-bottom: none;
    background: {palette.surface};
    color: {palette.text_muted};
}}

QTabBar::tab:first {{
    border-top-left-radius: 5px;
}}

QTabBar::tab:last {{
    border-top-right-radius: 5px;
}}

QTabBar::tab:hover {{
    background: {palette.accent_soft};
    color: {palette.accent_hover};
}}

QTabBar::tab:selected {{
    border-color: {palette.accent};
    border-bottom: 2px solid {palette.accent};
    background: {palette.window};
    color: {palette.accent_hover};
}}

/* Menus */

QMenu {{
    padding: 5px;
    border: 1px solid {palette.accent};
    border-radius: 5px;
    background: {palette.surface};
    color: {palette.text};
}}

QMenu::item {{
    min-width: 150px;
    padding: 6px 28px 6px 10px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background: {palette.selection};
    color: {palette.selection_text};
}}

QMenu::item:disabled {{
    color: {palette.disabled_text};
}}

QMenu::separator {{
    height: 1px;
    margin: 5px 8px;
    background: {palette.border};
}}

/* Progress bars */

QProgressBar {{
    min-height: 18px;
    border: 1px solid {palette.border};
    border-radius: 5px;
    background: {palette.input};
    color: {palette.text};
    text-align: center;
}}

QProgressBar::chunk {{
    border-radius: 4px;
    background: {palette.accent};
}}

/* Splitters */

QSplitter::handle {{
    background: {palette.border};
}}

QSplitter::handle:hover {{
    background: {palette.accent};
}}

QSplitter::handle:horizontal {{
    width: 3px;
}}

QSplitter::handle:vertical {{
    height: 3px;
}}

/* Scrollbars */

QScrollBar:vertical {{
    width: 12px;
    margin: 0;
    border: none;
    background: {palette.window};
}}

QScrollBar::handle:vertical {{
    min-height: 24px;
    border-radius: 5px;
    background: {palette.border};
}}

QScrollBar::handle:vertical:hover {{
    background: {palette.accent};
}}

QScrollBar:horizontal {{
    height: 12px;
    margin: 0;
    border: none;
    background: {palette.window};
}}

QScrollBar::handle:horizontal {{
    min-width: 24px;
    border-radius: 5px;
    background: {palette.border};
}}

QScrollBar::handle:horizontal:hover {{
    background: {palette.accent};
}}

QScrollBar::add-line,
QScrollBar::sub-line,
QScrollBar::add-page,
QScrollBar::sub-page {{
    width: 0;
    height: 0;
    border: none;
    background: transparent;
}}

/* Labels and tooltips */

QLabel {{
    background: transparent;
}}

QToolTip {{
    padding: 5px;
    border: 1px solid {palette.accent};
    border-radius: 4px;
    background: {palette.tooltip};
    color: {palette.text};
}}
"""


def dark_theme():
    return build_theme(DARK_PALETTE)


def light_theme():
    return build_theme(LIGHT_PALETTE)


def dark_blue_orange_theme():
    return build_theme(DARK_BLUE_ORANGE_PALETTE)