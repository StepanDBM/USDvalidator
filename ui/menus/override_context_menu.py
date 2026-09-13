from PySide6.QtWidgets import QMenu


class OverrideContextMenu(QMenu):
    def __init__(self, override, edit, toggle, remove, parent=None):
        super().__init__(parent)
        self.override = override
        self.edit_callback = edit
        self.toggle_callback = toggle
        self.remove_callback = remove
        self._build()

    def _build(self):
        self.addAction("Edit Override...").triggered.connect(self.edit_callback)
        toggle_label = (
            "Disable Override" if self.override.enabled else "Enable Override"
        )
        self.addAction(toggle_label).triggered.connect(self.toggle_callback)
        self.addAction("Remove Override").triggered.connect(self.remove_callback)
