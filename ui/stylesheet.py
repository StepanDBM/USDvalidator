# ui/stylesheet.py

DARK_THEME = """
QMainWindow {
    background: #202124;
}

QWidget {
    color: #e8eaed;
    font-size: 13px;
}

QPushButton {
    padding: 6px 14px;
    border: 1px solid #5f6368;
    border-radius: 4px;
    background: #303134;
}

QPushButton:hover {
    background: #3c4043;
}

QPushButton:pressed {
    background: #202124;
}

QComboBox {
    padding: 5px 8px;
    border: 1px solid #5f6368;
    border-radius: 4px;
    background: #303134;
}

QTextEdit {
    border: 1px solid #5f6368;
    border-radius: 4px;
    background: #171717;
}
"""


LIGHT_THEME = """
QMainWindow {
    background: #f5f5f5;
}

QWidget {
    color: #202124;
    font-size: 13px;
}

QPushButton {
    padding: 6px 14px;
    border: 1px solid #b0b0b0;
    border-radius: 4px;
    background: #ffffff;
}

QPushButton:hover {
    background: #eeeeee;
}

QPushButton:pressed {
    background: #dddddd;
}

QComboBox {
    padding: 5px 8px;
    border: 1px solid #b0b0b0;
    border-radius: 4px;
    background: #ffffff;
}

QTextEdit {
    border: 1px solid #b0b0b0;
    border-radius: 4px;
    background: #ffffff;
}
"""


def dark_theme():
    return DARK_THEME


def light_theme():
    return LIGHT_THEME