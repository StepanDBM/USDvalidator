from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QWidget,
)


from s_usd_desktop.ui.tooltips import TooltipText


class ProfileSelector(QWidget):
    def __init__(
        self,
        profile_loader,
        parent=None,
    ):
        super().__init__(parent)

        self.profile_loader = profile_loader

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(
            QLabel("Profile:")
        )

        self.combo = QComboBox()
        self.combo.setToolTip(TooltipText.PROFILE_SELECTOR)
        self.combo.setMinimumWidth(180)

        layout.addWidget(
            self.combo
        )

    def refresh(self):
        current_name = self.get_profile_name()

        self.combo.blockSignals(True)
        self.combo.clear()

        for name in (
            self.profile_loader
            .get_profile_names()
        ):
            self.combo.addItem(name)

        index = self.combo.findText(
            current_name
        )

        if index < 0 and self.combo.count():
            index = 0

        if index >= 0:
            self.combo.setCurrentIndex(index)

        self.combo.blockSignals(False)

    def get_profile_name(self):
        return self.combo.currentText()

    def get_profile(self):
        name = self.get_profile_name()

        if not name:
            return None

        return self.profile_loader.get_profile(
            name
        )