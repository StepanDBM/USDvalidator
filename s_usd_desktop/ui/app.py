# ui/app.py

import sys

from PySide6.QtWidgets import QApplication

from .main_window import MainWindow


def main():
    application = QApplication(sys.argv)
    application.setStyle("Fusion")

    window = MainWindow()
    window.show()

    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())