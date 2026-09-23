from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView, QMenu, QTreeWidget, QTreeWidgetItem


from s_usd_desktop.ui.tooltips import TooltipText


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

IMPACT_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
    "INFORMATIONAL": 4,
}


class SemanticChangesTree(QTreeWidget):
    change_selected = Signal(object)
    open_in_viewport_requested = Signal(object, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.comparison = None
        self.show_unchanged = False
        self.filters = {}
        self.setToolTip(TooltipText.COMPARISON_SEMANTIC_TREE)
        self.setHeaderLabels([
            "Domain",
            "Path",
            "Change",
            "Kind",
            "Impact",
            "Previous",
            "Current",
        ])
        self.setRootIsDecorated(False)
        self.setItemsExpandable(False)
        self.setIndentation(0)
        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.setColumnWidth(0, 110)
        self.setColumnWidth(1, 230)
        self.setColumnWidth(2, 240)
        self.setColumnWidth(3, 95)
        self.setColumnWidth(4, 95)
        self.setColumnWidth(5, 150)
        self.setColumnWidth(6, 150)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.currentItemChanged.connect(self._on_current_changed)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def set_comparison(self, comparison, show_unchanged=False, filters=None):
        self.comparison = comparison
        self.show_unchanged = show_unchanged
        self.filters = filters or {}
        self._rebuild()

    def set_filters(self, filters):
        self.filters = filters or {}
        self._rebuild()

    def _rebuild(self):
        self.clear()
        if self.comparison is None:
            return

        changes = sorted(
            (change for change in self.comparison.changes if self._visible(change)),
            key=self._sort_key,
        )
        for change in changes:
            domain = change.domain or change.category
            item = QTreeWidgetItem([
                domain,
                change.path,
                change.label,
                change.kind.value,
                change.impact.value,
                self._value(change.previous),
                self._value(change.current),
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, change)
            change_tooltip = (
                f"{TooltipText.COMPARISON_CHANGE_ROW}\n\n"
                f"Domain: {domain}\n"
                f"Subject: {change.path}\n"
                f"Change: {change.label}\n"
                f"Kind: {change.kind.value}\n"
                f"Impact: {change.impact.value}\n"
                f"Previous: {self._value(change.previous)}\n"
                f"Current: {self._value(change.current)}\n"
                f"Why it matters: {change.why_it_matters or 'Semantic stage content changed.'}"
            )
            for column in range(self.columnCount()):
                item.setToolTip(column, change_tooltip)
            item.setForeground(3, QColor(KIND_COLORS[change.kind.value]))
            self.addTopLevelItem(item)

    def _visible(self, change):
        if not self.show_unchanged and change.kind.value == "UNCHANGED":
            return False
        if self.filters.get("impact") and change.impact.value != self.filters["impact"]:
            return False

        domain = change.domain or change.category
        if self.filters.get("domain") and domain != self.filters["domain"]:
            return False
        if self.filters.get("kind") and change.kind.value != self.filters["kind"]:
            return False
        return not self.filters.get("regressions_only") or change.kind.value == "REGRESSION"

    @staticmethod
    def _sort_key(change):
        return (
            IMPACT_ORDER.get(change.impact.value, 99),
            change.domain or change.category,
            change.path,
            change.label,
        )

    @staticmethod
    def _value(value):
        if value is None:
            return ""
        text = str(value)
        return text if len(text) <= 140 else text[:137] + "..."

    def _on_current_changed(self, current, previous):
        change = current.data(0, Qt.ItemDataRole.UserRole) if current else None
        self.change_selected.emit(change)

    def _show_context_menu(self, position):
        item = self.itemAt(position)
        change = item.data(0, Qt.ItemDataRole.UserRole) if item else None
        if change is None:
            return

        menu = QMenu(self)
        automatic = "Previous" if change.kind.value == "REMOVED" else "Current"
        action = menu.addAction(f"Open and Frame in Viewport ({automatic})")
        action.setToolTip(
            "Open the automatically selected comparison side in Viewport and "
            "frame the prim associated with this semantic change."
        )
        action.triggered.connect(
            lambda checked=False, value=change: self.open_in_viewport_requested.emit(value, "auto")
        )
        menu.addSeparator()
        previous = menu.addAction("Open Previous in Viewport")
        current = menu.addAction("Open Current in Viewport")
        previous.setToolTip(TooltipText.COMPARISON_PREVIOUS_SOURCE)
        current.setToolTip(TooltipText.COMPARISON_CURRENT_SOURCE)
        previous.triggered.connect(
            lambda checked=False, value=change: self.open_in_viewport_requested.emit(value, "previous")
        )
        current.triggered.connect(
            lambda checked=False, value=change: self.open_in_viewport_requested.emit(value, "current")
        )
        menu.exec(self.viewport().mapToGlobal(position))
