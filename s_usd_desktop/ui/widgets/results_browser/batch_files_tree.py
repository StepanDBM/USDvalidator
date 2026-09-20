from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView, QTreeWidget, QTreeWidgetItem

from s_usd_core.batch.discovery_tree import build_report_tree


class BatchFilesTree(QTreeWidget):
    report_selected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["Discovered Source", "Status", "Files"])
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setUniformRowHeights(True)
        self.setColumnWidth(0, 300)
        self.setColumnWidth(1, 90)
        self.setColumnWidth(2, 55)
        self.currentItemChanged.connect(self._emit_current)

    def set_reports(self, reports, root=None):
        self.blockSignals(True)
        self.clear()
        node = build_report_tree(reports, root)
        root_item = self._directory_item(node)
        self.addTopLevelItem(root_item)
        self._populate(root_item, node)
        root_item.setExpanded(True)
        self.resizeColumnToContents(0)
        first = self._first_file(root_item)
        self.blockSignals(False)
        if first:
            self.setCurrentItem(first)
            self._emit_current(first, None)

    def selected_report(self):
        item = self.currentItem()
        return item.data(0, Qt.ItemDataRole.UserRole) if item else None

    def _populate(self, parent_item, node):
        for child in sorted(node.directories.values(), key=lambda value: value.name.lower()):
            item = self._directory_item(child)
            parent_item.addChild(item)
            self._populate(item, child)
        for report in sorted(node.reports, key=lambda value: Path(value.source_path).name.lower()):
            passed = bool(report.publish_passed)
            item = QTreeWidgetItem([
                Path(report.source_path).name,
                "PASSED" if passed else "FAILED",
                "",
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, report)
            item.setToolTip(0, str(report.source_path))
            item.setForeground(1, QColor("#4CAF50" if passed else "#F44336"))
            parent_item.addChild(item)

    @staticmethod
    def _directory_item(node):
        status = "PASSED" if not node.failed_count else "FAILED"
        item = QTreeWidgetItem([node.name, status, str(node.file_count)])
        item.setToolTip(0, str(node.path))
        item.setForeground(1, QColor("#4CAF50" if not node.failed_count else "#F44336"))
        item.setData(0, Qt.ItemDataRole.UserRole + 1, str(node.path))
        return item

    def _emit_current(self, current, previous):
        report = current.data(0, Qt.ItemDataRole.UserRole) if current else None
        if report is not None:
            self.report_selected.emit(report)

    def _first_file(self, item):
        if item.data(0, Qt.ItemDataRole.UserRole) is not None:
            return item
        for index in range(item.childCount()):
            found = self._first_file(item.child(index))
            if found:
                return found
        return None
