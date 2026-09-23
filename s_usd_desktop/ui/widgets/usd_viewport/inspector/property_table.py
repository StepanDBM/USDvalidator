from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLineEdit, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from pxr import Usd, UsdGeom

from ..viewport_models import PropertyRow


from s_usd_desktop.ui.tooltips import TooltipText


class PropertyTable(QWidget):
    property_selected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows = []
        self._prim = None
        self._time = Usd.TimeCode.Default()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search properties...")
        self.table = QTableWidget(0, 3)
        self.search.setToolTip(
            "Filter the selected prim's properties by name, type, or displayed value."
        )
        self.table.setToolTip(TooltipText.VIEWPORT_PRIM_INSPECTOR)
        self.table.setHorizontalHeaderLabels(["Type", "Property Name", "Value"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 48)
        self.table.setColumnWidth(1, 250)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.search)
        layout.addWidget(self.table, 1)
        self.search.textChanged.connect(self._rebuild)
        self.table.currentCellChanged.connect(self._emit_current)

    def set_prim(self, prim):
        self._rows = self._build_rows(prim) if prim and prim.IsValid() else []
        self._rebuild()

    def set_current_time(self, value):
        self._time = Usd.TimeCode(float(value))
        if self._prim:
            self._rows = self._build_rows(self._prim)
            self._rebuild()

    def selected_time_samples(self):
        row = self.table.currentRow()
        item = self.table.item(row, 0) if row >= 0 else None
        data = item.data(Qt.ItemDataRole.UserRole) if item else None
        if not data or data.kind != "A" or not self._prim:
            return ()
        attribute = self._prim.GetAttribute(data.name)
        return tuple(attribute.GetTimeSamples()) if attribute else ()

    def select_property(self, property_path):
        name = str(property_path).rsplit(".", 1)[-1]
        self.search.clear()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            if item and item.text() == name:
                self.table.setCurrentCell(row, 1)
                self.table.scrollToItem(item)
                return True
        return False

    def _build_rows(self, prim):
        rows = [
            PropertyRow("C", "Prim Path", prim.GetPath().pathString, prim.GetPath()),
            PropertyRow("C", "Schema Type", prim.GetTypeName() or "typeless", prim.GetTypeName()),
            PropertyRow("C", "Active", str(prim.IsActive()), prim.IsActive()),
            PropertyRow("C", "Instanceable", str(prim.IsInstanceable()), prim.IsInstanceable()),
        ]
        imageable = UsdGeom.Imageable(prim)
        if imageable:
            rows.extend([
                PropertyRow("C", "Resolved Visibility", str(imageable.ComputeVisibility()), imageable.ComputeVisibility()),
                PropertyRow("C", "Purpose", str(imageable.ComputePurpose()), imageable.ComputePurpose()),
            ])
        for attribute in sorted(prim.GetAttributes(), key=lambda value: value.GetName()):
            try:
                value = attribute.Get(self._time)
            except Exception as error:
                value = f"<unavailable: {error}>"
            samples = tuple(attribute.GetTimeSamples())
            kind = "A*" if samples else "A"
            summary = f"{_short(value)}  [{len(samples)} samples]" if samples else _short(value)
            rows.append(PropertyRow(kind, attribute.GetName(), summary, value))
        for relationship in sorted(prim.GetRelationships(), key=lambda value: value.GetName()):
            value = tuple(path.pathString for path in relationship.GetTargets())
            rows.append(PropertyRow("R", relationship.GetName(), _short(value), value))
        return rows

    def _rebuild(self):
        query = self.search.text().strip().lower()
        visible = [row for row in self._rows if not query or query in row.name.lower() or query in row.value.lower()]
        self.table.setRowCount(len(visible))
        for row_index, row in enumerate(visible):
            for column, value in enumerate((row.kind, row.name, row.value)):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, row)
                item.setToolTip(
                    f"{TooltipText.VIEWPORT_PROPERTY_ROW}\n\n"
                    f"Kind: {row.kind}\n"
                    f"Property: {row.name}\n"
                    f"Value: {row.value}"
                )
                self.table.setItem(row_index, column, item)
        if visible:
            self.table.selectRow(0)

    def _emit_current(self, row, column, previous_row, previous_column):
        item = self.table.item(row, 0) if row >= 0 else None
        self.property_selected.emit(item.data(Qt.ItemDataRole.UserRole) if item else None)


def _short(value):
    text = str(value)
    return text if len(text) <= 180 else text[:177] + "..."
