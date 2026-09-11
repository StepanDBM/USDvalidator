import sys

from PySide6.QtWidgets import QApplication

from .main_window import MainWindow
from .stylesheet import dark_theme, light_theme


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(dark_theme())
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()