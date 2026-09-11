from PySide6.QtWidgets import QComboBox, QLabel, QVBoxLayout, QWidget

from validation.profiles import DEFAULT_PROFILE


class ProfileSelector(QWidget):
    def __init__(self, profile_loader, parent=None):
        super().__init__(parent)

        self.profile_loader = profile_loader

        self._build_ui()
        self._load_profiles()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Profile"))

        self.combo = QComboBox()
        layout.addWidget(self.combo)

    def _load_profiles(self):
        for name in self.profile_loader.get_profile_names():
            self.combo.addItem(name)

        index = self.combo.findText(DEFAULT_PROFILE)

        if index >= 0:
            self.combo.setCurrentIndex(index)

    def get_profile(self):
        return self.profile_loader.get_profile(
            self.combo.currentText()
        )

    def get_profile_name(self):
        return self.combo.currentText()