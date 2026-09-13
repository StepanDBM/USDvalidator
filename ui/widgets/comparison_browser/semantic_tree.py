from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem


KIND_COLORS = {
    "ADDED": "#3fb950",
    "REMOVED": "#f85149",
    "REGRESSION": "#f85149",
    "RESOLVED": "#3fb950",
    "CHANGED": "#d29922",
    "INCREASED": "#d29922",
    "DECREASED": "#58a6ff",
    "UNCHANGED": "#8b949e",
}


class SemanticChangesTree(QTreeWidget):
    change_selected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["Change", "Kind", "Previous", "Current", "Path"])
        self.setColumnWidth(0, 240)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 150)
        self.setColumnWidth(3, 150)
        self.currentItemChanged.connect(self._on_current_changed)

    def set_comparison(self, comparison, show_unchanged=False):
        self.clear()
        grouped = {}
        for change in comparison.changes:
            if not show_unchanged and change.kind.value == "UNCHANGED":
                continue
            grouped.setdefault(change.category, []).append(change)

        for category in sorted(grouped):
            category_item = QTreeWidgetItem([category])
            category_item.setFirstColumnSpanned(True)
            self.addTopLevelItem(category_item)
            for change in grouped[category]:
                item = QTreeWidgetItem([
                    change.label,
                    change.kind.value,
                    self._value(change.previous),
                    self._value(change.current),
                    change.path,
                ])
                item.setData(0, Qt.ItemDataRole.UserRole, change)
                item.setForeground(1, QColor(KIND_COLORS[change.kind.value]))
                category_item.addChild(item)
            category_item.setExpanded(True)

    @staticmethod
    def _value(value):
        if value is None:
            return ""
        text = str(value)
        return text if len(text) <= 140 else text[:137] + "..."

    def _on_current_changed(self, current, previous):
        change = current.data(0, Qt.ItemDataRole.UserRole) if current else None
        self.change_selected.emit(change)
