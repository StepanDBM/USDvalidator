from __future__ import annotations

from PySide6.QtCore import QItemSelectionModel, Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QAbstractItemView, QLineEdit, QTreeView, QVBoxLayout, QWidget

from .outliner_model import PrimOutlinerModel
from .outliner_proxy import PrimOutlinerProxy
from .outliner_row import PrimRowDelegate


class StageOutliner(QWidget):
    paths_selected = Signal(object, str)
    visibility_requested = Signal(object, bool)
    frame_requested = Signal()
    hide_requested = Signal()
    show_requested = Signal()
    show_all_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.primary_path = ""
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Search prim name, path or type...")
        self.tree = QTreeView()
        self.tree.setAlternatingRowColors(True)
        self.tree.setUniformRowHeights(True)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.model = PrimOutlinerModel(self)
        self.proxy = PrimOutlinerProxy(self)
        self.proxy.setSourceModel(self.model)
        self.tree.setModel(self.proxy)
        self.tree.setItemDelegate(PrimRowDelegate(self.tree))
        self.tree.setColumnWidth(0, 240)
        self.tree.setColumnWidth(1, 100)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.filter_edit)
        layout.addWidget(self.tree, 1)

        self.filter_edit.textChanged.connect(self._set_filter)
        self.model.visibility_requested.connect(
            lambda path, visible: self.visibility_requested.emit([path], visible)
        )
        self.tree.selectionModel().selectionChanged.connect(self._emit_selection)
        self.tree.clicked.connect(self._remember_primary)
        self._add_shortcuts()

    def set_stage(self, stage):
        self.primary_path = ""
        self.model.set_stage(stage)
        self.tree.expandToDepth(1)

    def set_hidden_paths(self, paths):
        self.model.set_hidden_paths(paths)

    def selected_paths(self):
        paths = []
        for index in self.tree.selectionModel().selectedRows(0):
            path = index.data(Qt.ItemDataRole.UserRole)
            if path:
                paths.append(path)
        return paths

    def select_path(self, path, additive=False):
        return self.select_paths([path], str(path), additive)

    def select_paths(self, paths, primary_path="", additive=False):
        selection = self.tree.selectionModel()
        if not additive:
            selection.clearSelection()
        first = None
        for path in paths:
            source_index = self.model.index_for_path(path, 0)
            index = self.proxy.mapFromSource(source_index)
            if not index.isValid():
                continue
            flags = QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows
            selection.select(index, flags)
            first = first or index
        primary = primary_path or (paths[-1] if paths else "")
        primary_index = self.proxy.mapFromSource(self.model.index_for_path(primary, 0))
        if primary_index.isValid():
            self.primary_path = primary
            selection.setCurrentIndex(primary_index, QItemSelectionModel.SelectionFlag.NoUpdate)
            self.tree.scrollTo(primary_index)
        elif first:
            self.tree.scrollTo(first)
        return bool(first or primary_index.isValid())

    def clear_selection(self):
        self.tree.clearSelection()
        self.primary_path = ""

    def _set_filter(self, value):
        expanded = self._expanded_paths()
        self.proxy.set_query(value)
        if value:
            self.tree.expandAll()
        else:
            self._restore_expanded_paths(expanded)

    def _remember_primary(self, index):
        path = index.data(Qt.ItemDataRole.UserRole)
        if path:
            self.primary_path = path
            self._emit_selection()

    def _emit_selection(self, *args):
        paths = self.selected_paths()
        if self.primary_path not in paths:
            current = self.tree.currentIndex()
            self.primary_path = current.data(Qt.ItemDataRole.UserRole) if current.isValid() else ""
        if paths:
            self.paths_selected.emit(paths, self.primary_path or paths[-1])

    def _add_shortcuts(self):
        shortcuts = (
            ("F", self.frame_requested),
            ("H", self.hide_requested),
            ("Shift+H", self.show_requested),
            ("Alt+H", self.show_all_requested),
        )
        self._shortcuts = []
        for sequence, signal in shortcuts:
            shortcut = QShortcut(QKeySequence(sequence), self)
            shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            shortcut.activated.connect(signal.emit)
            self._shortcuts.append(shortcut)

    def _expanded_paths(self):
        return {
            path for path in self.model.items
            if self.tree.isExpanded(self.proxy.mapFromSource(self.model.index_for_path(path, 0)))
        }

    def _restore_expanded_paths(self, paths):
        for path in paths:
            index = self.proxy.mapFromSource(self.model.index_for_path(path, 0))
            if index.isValid():
                self.tree.setExpanded(index, True)
