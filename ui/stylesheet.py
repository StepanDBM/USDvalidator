# ui/stylesheet.py


DARK_THEME = """
QMainWindow {
    background: #202124;
}

QWidget {
    color: #e8eaed;
    font-size: 13px;
    background: #202124;
}

QPushButton {
    padding: 6px 14px;
    border: 1px solid #5f6368;
    border-radius: 4px;
    background: #303134;
    color: #e8eaed;
}

QPushButton:hover {
    background: #3c4043;
}

QPushButton:pressed {
    background: #202124;
}

QPushButton:disabled {
    color: #80868b;
    background: #292a2d;
}

QComboBox,
QLineEdit {
    padding: 5px 8px;
    border: 1px solid #5f6368;
    border-radius: 4px;
    background: #303134;
    color: #e8eaed;
}

QComboBox:hover,
QLineEdit:focus {
    border: 1px solid #8ab4f8;
}

QComboBox QAbstractItemView {
    background: #303134;
    color: #e8eaed;
    selection-background-color: #3c4043;
    selection-color: #ffffff;
}

QTextEdit,
QListWidget,
QTreeWidget {
    border: 1px solid #5f6368;
    border-radius: 4px;
    background: #171717;
    color: #e8eaed;
}

QListWidget::item,
QTreeWidget::item {
    padding: 4px;
}

QListWidget::item:selected,
QTreeWidget::item:selected {
    background: #3c4043;
    color: #ffffff;
}

QGroupBox {
    border: 1px solid #5f6368;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    background: #202124;
}

QTabWidget::pane {
    border: 1px solid #5f6368;
}

QTabBar::tab {
    padding: 7px 14px;
    background: #303134;
    color: #e8eaed;
    border: 1px solid #5f6368;
}

QTabBar::tab:hover {
    background: #3c4043;
}

QTabBar::tab:selected {
    background: #202124;
}

QLabel {
    background: transparent;
}

QCheckBox {
    spacing: 6px;
}

QHeaderView::section {
    padding: 5px 8px;
    background: #303134;
    color: #e8eaed;
    border: 1px solid #5f6368;
}

QScrollBar:vertical,
QScrollBar:horizontal {
    background: #202124;
}

QToolTip {
    background: #303134;
    color: #e8eaed;
    border: 1px solid #5f6368;
    padding: 4px;
}
"""


LIGHT_THEME = """
QMainWindow {
    background: #f4f6f8;
}

QWidget {
    color: #202124;
    font-size: 13px;
    background: #f4f6f8;
}

QPushButton {
    padding: 6px 14px;
    border: 1px solid #b8bec6;
    border-radius: 4px;
    background: #ffffff;
    color: #202124;
}

QPushButton:hover {
    background: #e9edf2;
}

QPushButton:pressed {
    background: #dfe4ea;
}

QPushButton:disabled {
    color: #9aa0a6;
    background: #e6e9ed;
}

QComboBox,
QLineEdit {
    padding: 5px 8px;
    border: 1px solid #b8bec6;
    border-radius: 4px;
    background: #ffffff;
    color: #202124;
}

QComboBox:hover,
QLineEdit:focus {
    border: 1px solid #5f8fc4;
}

QComboBox QAbstractItemView {
    background: #ffffff;
    color: #202124;
    selection-background-color: #dce6f2;
    selection-color: #202124;
}

QTextEdit,
QListWidget,
QTreeWidget {
    border: 1px solid #b8bec6;
    border-radius: 4px;
    background: #ffffff;
    color: #202124;
}

QListWidget::item,
QTreeWidget::item {
    padding: 4px;
}

QListWidget::item:selected,
QTreeWidget::item:selected {
    background: #dce6f2;
    color: #202124;
}

QGroupBox {
    border: 1px solid #b8bec6;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    background: #f4f6f8;
}

QTabWidget::pane {
    border: 1px solid #b8bec6;
}

QTabBar::tab {
    padding: 7px 14px;
    background: #e9edf2;
    color: #202124;
    border: 1px solid #b8bec6;
}

QTabBar::tab:hover {
    background: #dfe4ea;
}

QTabBar::tab:selected {
    background: #f4f6f8;
}

QLabel {
    background: transparent;
}

QCheckBox {
    spacing: 6px;
}

QHeaderView::section {
    padding: 5px 8px;
    background: #e9edf2;
    color: #202124;
    border: 1px solid #b8bec6;
}

QScrollBar:vertical,
QScrollBar:horizontal {
    background: #f4f6f8;
}

QToolTip {
    background: #ffffff;
    color: #202124;
    border: 1px solid #b8bec6;
    padding: 4px;
}
"""


DARK_BLUE_ORANGE_THEME = """
QMainWindow {
    background: #0b1628;
}

QWidget {
    color: #f4f1ea;
    font-size: 13px;
    background: #0b1628;
}

QPushButton {
    padding: 6px 14px;
    border: 1px solid #c96f2d;
    border-radius: 4px;
    background: #12243d;
    color: #f4f1ea;
}

QPushButton:hover {
    background: #1a3152;
    border: 1px solid #e58a3a;
}

QPushButton:pressed {
    background: #09111f;
}

QPushButton:disabled {
    color: #66758a;
    background: #101c2e;
    border: 1px solid #34445a;
}

QComboBox,
QLineEdit {
    padding: 5px 8px;
    border: 1px solid #38506d;
    border-radius: 4px;
    background: #101f35;
    color: #f4f1ea;
}

QComboBox:hover,
QLineEdit:focus {
    border: 1px solid #e58a3a;
}

QComboBox QAbstractItemView {
    background: #101f35;
    color: #f4f1ea;
    selection-background-color: #c96f2d;
    selection-color: #ffffff;
}

QTextEdit,
QListWidget,
QTreeWidget {
    border: 1px solid #38506d;
    border-radius: 4px;
    background: #081321;
    color: #f4f1ea;
}

QListWidget::item,
QTreeWidget::item {
    padding: 4px;
}

QListWidget::item:selected,
QTreeWidget::item:selected {
    background: #243d5d;
    color: #ffffff;
}

QGroupBox {
    border: 1px solid #38506d;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    background: #0b1628;
    color: #e58a3a;
}

QTabWidget::pane {
    border: 1px solid #38506d;
}

QTabBar::tab {
    padding: 7px 14px;
    background: #12243d;
    color: #b9c5d4;
    border: 1px solid #38506d;
}

QTabBar::tab:hover {
    background: #1a3152;
    color: #f4f1ea;
}

QTabBar::tab:selected {
    background: #0b1628;
    color: #e58a3a;
    border-bottom: 2px solid #e58a3a;
}

QLabel {
    background: transparent;
}

QCheckBox {
    spacing: 6px;
}

QCheckBox::indicator:checked {
    background: #d97830;
    border: 1px solid #e58a3a;
}

QHeaderView::section {
    padding: 5px 8px;
    background: #12243d;
    color: #e58a3a;
    border: 1px solid #38506d;
}

QScrollBar:vertical,
QScrollBar:horizontal {
    background: #0b1628;
}

QToolTip {
    background: #12243d;
    color: #f4f1ea;
    border: 1px solid #e58a3a;
    padding: 4px;
}
"""


def dark_theme():
    return DARK_THEME


def light_theme():
    return LIGHT_THEME


def dark_blue_orange_theme():
    return DARK_BLUE_ORANGE_THEME