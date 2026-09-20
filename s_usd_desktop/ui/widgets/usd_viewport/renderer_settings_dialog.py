from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QLabel, QLineEdit, QScrollArea, QVBoxLayout, QWidget


class RendererSettingsDialog(QDialog):
    def __init__(self, viewport, parent=None):
        super().__init__(parent)
        self.viewport = viewport
        self.setWindowTitle("Hydra Renderer Settings")
        self.resize(540, 620)
        body = QWidget()
        form = QFormLayout(body)
        settings = viewport.renderer_settings()
        if not settings:
            form.addRow(QLabel("The active renderer exposes no editable settings."))
        for descriptor in settings:
            key = _descriptor_value(descriptor, "key", "name")
            label = _descriptor_value(descriptor, "displayName", "name", fallback=str(key))
            value = viewport.GetRendererSetting(key)
            editor = self._editor(key, value)
            form.addRow(f"{label}:", editor)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(body)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)
        layout.addWidget(buttons)

    def _editor(self, key, value):
        if isinstance(value, bool):
            editor = QCheckBox()
            editor.setChecked(value)
            editor.toggled.connect(lambda checked, k=key: self.viewport.set_renderer_setting(k, checked))
            return editor
        if isinstance(value, (int, float)):
            editor = QDoubleSpinBox()
            editor.setRange(-1_000_000, 1_000_000)
            editor.setDecimals(5)
            editor.setValue(float(value))
            editor.valueChanged.connect(lambda number, k=key, original=value: self.viewport.set_renderer_setting(k, type(original)(number)))
            return editor
        editor = QLineEdit(str(value))
        editor.editingFinished.connect(lambda e=editor, k=key: self.viewport.set_renderer_setting(k, e.text()))
        return editor


def _descriptor_value(descriptor, *names, fallback=""):
    for name in names:
        if hasattr(descriptor, name):
            return getattr(descriptor, name)
    return fallback
