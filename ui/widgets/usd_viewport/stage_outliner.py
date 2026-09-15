from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLineEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget


class StageOutliner(QWidget):
    path_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = {}
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filter prims...")
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Prim", "Type"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setUniformRowHeights(True)
        self.tree.setColumnWidth(0, 210)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.filter_edit)
        layout.addWidget(self.tree, 1)

        self.filter_edit.textChanged.connect(self._filter)
        self.tree.currentItemChanged.connect(self._on_current_changed)

    def set_stage(self, stage):
        self.tree.clear()
        self._items.clear()
        if not stage:
            return
        for prim in stage.GetPseudoRoot().GetChildren():
            self._add_prim(prim, self.tree.invisibleRootItem())
        self.tree.expandToDepth(1)

    def select_path(self, path):
        item = self._items.get(str(path))
        if not item:
            return False
        self.tree.blockSignals(True)
        self.tree.setCurrentItem(item)
        item.setSelected(True)
        self.tree.scrollToItem(item)
        self.tree.blockSignals(False)
        return True

    def _add_prim(self, prim, parent):
        path = prim.GetPath().pathString
        item = QTreeWidgetItem([prim.GetName(), prim.GetTypeName() or "typeless"])
        item.setData(0, Qt.ItemDataRole.UserRole, path)
        parent.addChild(item)
        self._items[path] = item
        for child in prim.GetChildren():
            self._add_prim(child, item)

    def _on_current_changed(self, current, previous):
        if current:
            self.path_selected.emit(current.data(0, Qt.ItemDataRole.UserRole))

    def _filter(self, text):
        query = text.strip().lower()
        for path, item in self._items.items():
            matches = not query or query in path.lower() or query in item.text(1).lower()
            item.setHidden(not matches and not self._has_matching_descendant(item, query))

    def _has_matching_descendant(self, item, query):
        for index in range(item.childCount()):
            child = item.child(index)
            path = child.data(0, Qt.ItemDataRole.UserRole).lower()
            if query in path or query in child.text(1).lower() or self._has_matching_descendant(child, query):
                return True
        return False
