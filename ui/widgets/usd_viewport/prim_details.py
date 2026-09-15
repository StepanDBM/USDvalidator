from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QLabel, QScrollArea, QVBoxLayout, QWidget


class PrimDetails(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = QLabel("No prim selected")
        self.title.setStyleSheet("font-weight: 600; font-size: 14px;")
        self.content = QWidget()
        self.form = QFormLayout(self.content)
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.content)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(self.title)
        layout.addWidget(scroll, 1)

    def set_prim(self, prim):
        self._clear()
        if not prim or not prim.IsValid():
            self.title.setText("No prim selected")
            return

        self.title.setText(prim.GetPath().pathString)
        self._row("Name", prim.GetName())
        self._row("Type", prim.GetTypeName() or "typeless")
        self._row("Kind", prim.GetMetadata("kind") or "")
        self._row("Active", prim.IsActive())
        self._row("Defined", prim.IsDefined())
        self._row("Instance", prim.IsInstance())
        self._row("Instanceable", prim.IsInstanceable())
        self._row("Applied schemas", ", ".join(str(value) for value in prim.GetAppliedSchemas()))
        self._row("Properties", len(prim.GetProperties()))
        self._row("Children", len(prim.GetChildren()))

        for attribute in sorted(prim.GetAttributes(), key=lambda value: value.GetName()):
            self._row(attribute.GetName(), self._attribute_value(attribute))
        for relationship in sorted(prim.GetRelationships(), key=lambda value: value.GetName()):
            targets = ", ".join(path.pathString for path in relationship.GetTargets())
            self._row(relationship.GetName(), targets or "<no targets>")

    @staticmethod
    def _attribute_value(attribute):
        try:
            value = attribute.Get()
        except Exception as error:
            return f"<unavailable: {error}>"
        text = str(value)
        return text if len(text) <= 220 else text[:217] + "..."

    def _row(self, label, value):
        field = QLabel(str(value))
        field.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        field.setWordWrap(True)
        self.form.addRow(f"{label}:", field)

    def _clear(self):
        while self.form.rowCount():
            self.form.removeRow(0)
