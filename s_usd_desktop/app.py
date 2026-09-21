import sys

from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow
from .ui.storage import install_storage_workspace


def main():
    application = QApplication(sys.argv)
    application.setOrganizationName("Styopa")
    application.setApplicationName("S-USDv")
    application.setStyle("Fusion")

    window = MainWindow()
    install_storage_workspace(window)
    window.show()

    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
