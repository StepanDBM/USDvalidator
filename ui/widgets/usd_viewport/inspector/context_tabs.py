from __future__ import annotations

import json

from PySide6.QtWidgets import QAbstractItemView, QPlainTextEdit, QTableWidget, QTableWidgetItem, QTabWidget
from pxr import UsdShade


class ContextTabs(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = _text_view()
        self.metadata = _table(["Metadata", "Value"])
        self.layers = _table(["Layer", "Path", "Specifier"])
        self.composition = _table(["Layer", "Arc / Spec", "Path", "Has Spec"])
        self.materials = _table(["Purpose", "Material", "Relationship"])
        self.validation = _table(["Status", "Check", "Message"])
        self.semantic = _table(["Field", "Value"])
        self.addTab(self.value, "Value")
        self.addTab(self.metadata, "Metadata")
        self.addTab(self.layers, "Layer Stack")
        self.addTab(self.composition, "Composition")
        self.addTab(self.materials, "Materials")
        self.addTab(self.validation, "Validation")
        self.addTab(self.semantic, "Semantic Change")

    def set_prim(self, prim):
        self.value.clear()
        for table in (self.metadata, self.layers, self.composition, self.materials, self.validation, self.semantic):
            table.setRowCount(0)
        if not prim or not prim.IsValid():
            return
        self._set_metadata(prim)
        self._set_prim_stack(prim)
        self._set_materials(prim)

    def set_property(self, row):
        if row is None:
            self.value.clear()
            return
        value = row.raw_value
        if isinstance(value, (dict, list, tuple)):
            try:
                text = json.dumps(value, indent=2, default=str)
            except TypeError:
                text = str(value)
        else:
            text = str(value)
        self.value.setPlainText(text)

    def show_validation_results(self, results, selected=None):
        rows = [(item.status.value, item.check_id, item.message) for item in results]
        _fill(self.validation, rows)
        self.setCurrentWidget(self.validation)
        if selected in results:
            row = list(results).index(selected)
            self.validation.selectRow(row)
            self.validation.scrollToItem(self.validation.item(row, 0))

    def show_semantic_change(self, change, side):
        rows = [
            ("Side", side.title()),
            ("Kind", change.kind.value),
            ("Impact", change.impact.value),
            ("Domain", change.domain or change.category),
            ("Path", change.path),
            ("Property", change.property_path),
            ("Change", change.label),
            ("Previous", change.previous),
            ("Current", change.current),
            ("Why it matters", change.why_it_matters),
            ("Validation consequence", change.validation_consequence),
        ]
        _fill(self.semantic, rows)
        self.setCurrentWidget(self.semantic)

    def _set_metadata(self, prim):
        rows = []
        for key in prim.GetAllMetadata():
            rows.append((str(key), str(prim.GetMetadata(key))))
        rows.extend(("Applied Schema", str(value)) for value in prim.GetAppliedSchemas())
        _fill(self.metadata, rows)

    def _set_prim_stack(self, prim):
        layers = []
        composition = []
        for spec in prim.GetPrimStack():
            layer = spec.layer.identifier
            path = spec.path.pathString
            specifier = str(spec.specifier).split(".")[-1]
            layers.append((layer, path, specifier))
            composition.append((layer, specifier, path, "yes"))
        _fill(self.layers, layers)
        _fill(self.composition, composition)

    def _set_materials(self, prim):
        rows = []
        api = UsdShade.MaterialBindingAPI(prim)
        for purpose in (UsdShade.Tokens.preview, UsdShade.Tokens.full, UsdShade.Tokens.allPurpose):
            try:
                material, relationship = api.ComputeBoundMaterial(purpose)
            except Exception:
                continue
            material_path = material.GetPath().pathString if material else "<unbound>"
            relationship_path = relationship.GetPath().pathString if relationship else ""
            rows.append((str(purpose), material_path, relationship_path))
        _fill(self.materials, rows)


def _text_view():
    widget = QPlainTextEdit()
    widget.setReadOnly(True)
    return widget


def _table(headers):
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.horizontalHeader().setStretchLastSection(True)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    return table


def _fill(table, rows):
    table.setRowCount(len(rows))
    for row_index, row in enumerate(rows):
        for column, value in enumerate(row):
            table.setItem(row_index, column, QTableWidgetItem(str(value)))
