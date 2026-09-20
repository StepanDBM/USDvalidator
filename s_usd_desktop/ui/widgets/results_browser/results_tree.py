import json

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QMenu, QTreeWidget, QTreeWidgetItem


STATUS_COLORS = {
    "PASSED": "#4CAF50",
    "FAILED": "#F44336",
    "ERROR": "#F44336",
    "SKIPPED": "#A0A0A0",
}


class ResultsTree(QTreeWidget):
    result_selected = Signal(object)
    open_in_viewport_requested = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.results = ()
        self.setHeaderLabels(["Check", "Status", "Severity", "Location", "Message"])
        self.setColumnWidth(0, 260)
        self.setColumnWidth(1, 85)
        self.setColumnWidth(2, 85)
        self.setColumnWidth(3, 180)
        self.setAlternatingRowColors(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.currentItemChanged.connect(self._on_item_changed)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def set_results(self, results, filters=None):
        self.results = tuple(results)
        filters = filters or {}
        grouped = {}
        for result in self.results:
            if self._matches(result, filters):
                grouped.setdefault(result.category or "Uncategorized", []).append(result)

        self.clear()
        for category in sorted(grouped):
            category_item = QTreeWidgetItem([category])
            category_item.setFirstColumnSpanned(True)
            self.addTopLevelItem(category_item)
            for result in grouped[category]:
                item = QTreeWidgetItem([
                    result.label,
                    result.status.value,
                    result.severity.value,
                    result.location,
                    result.message,
                ])
                item.setData(0, Qt.ItemDataRole.UserRole, result)
                item.setToolTip(0, result.check_id)
                item.setForeground(1, QColor(STATUS_COLORS[result.status.value]))
                category_item.addChild(item)
            category_item.setExpanded(True)

        if self.topLevelItemCount():
            first = self.topLevelItem(0)
            if first.childCount():
                self.setCurrentItem(first.child(0))
        else:
            self.result_selected.emit(None)

    @staticmethod
    def _matches(result, filters):
        status = filters.get("status", "All Statuses")
        severity = filters.get("severity", "All Severities")
        category = filters.get("category", "All Categories")
        search = filters.get("search", "")
        if status != "All Statuses" and result.status.value != status:
            return False
        if severity != "All Severities" and result.severity.value != severity:
            return False
        if category != "All Categories" and result.category != category:
            return False
        searchable = " ".join([
            result.check_id,
            result.label,
            result.category,
            result.message,
            result.location,
            result.layer,
            result.suggestion,
        ]).lower()
        return not search or search in searchable

    def _on_item_changed(self, current, previous):
        result = current.data(0, Qt.ItemDataRole.UserRole) if current else None
        self.result_selected.emit(result)

    def _show_context_menu(self, position):
        item = self.itemAt(position)
        result = item.data(0, Qt.ItemDataRole.UserRole) if item else None
        if result is None:
            return
        menu = QMenu(self)
        open_action = menu.addAction("Open and Frame in Viewport")
        open_action.setEnabled(True)
        open_action.triggered.connect(lambda checked=False, value=result: self.open_in_viewport_requested.emit(value))
        menu.addSeparator()
        actions = {
            "Copy Check ID": result.check_id,
            "Copy Message": result.message,
            "Copy Location": result.location,
            "Copy Details as JSON": json.dumps(
                result.details, indent=2, ensure_ascii=False, default=str
            ),
        }
        for label, value in actions.items():
            action = menu.addAction(label)
            action.setEnabled(bool(value))
            action.triggered.connect(
                lambda checked=False, text=str(value):
                QApplication.clipboard().setText(text)
            )
        menu.exec(self.viewport().mapToGlobal(position))
