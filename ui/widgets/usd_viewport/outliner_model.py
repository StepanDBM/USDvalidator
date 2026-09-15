from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, Signal


@dataclass
class PrimTreeItem:
    prim: object = None
    parent: "PrimTreeItem | None" = None
    children: list["PrimTreeItem"] = field(default_factory=list)

    @property
    def path(self):
        return self.prim.GetPath().pathString if self.prim else ""

    @property
    def name(self):
        return self.prim.GetName() if self.prim else ""

    @property
    def type_name(self):
        return self.prim.GetTypeName() or "typeless" if self.prim else ""


class PrimOutlinerModel(QAbstractItemModel):
    visibility_requested = Signal(str, bool)
    headers = ("Prim", "Type")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root = PrimTreeItem()
        self.stage = None
        self.items = {}
        self.hidden_paths = set()

    def set_stage(self, stage):
        self.beginResetModel()
        self.stage = stage
        self.root = PrimTreeItem()
        self.items = {}
        self.hidden_paths = set()
        if stage:
            for prim in stage.GetPseudoRoot().GetChildren():
                self._append_prim(prim, self.root)
        self.endResetModel()

    def set_hidden_paths(self, paths):
        self.hidden_paths = set(paths)
        self._emit_all_rows_changed()

    def request_visibility(self, path):
        self.visibility_requested.emit(path, self.is_effectively_hidden(path))

    def is_hidden(self, path):
        return path in self.hidden_paths

    def is_effectively_hidden(self, path):
        current = path
        while current and current != "/":
            if current in self.hidden_paths:
                return True
            current = current.rsplit("/", 1)[0]
        return False

    def is_hidden_by_ancestor(self, path):
        parent = path.rsplit("/", 1)[0]
        return bool(parent and self.is_effectively_hidden(parent))

    def item_for_path(self, path):
        return self.items.get(str(path))

    def index_for_path(self, path, column=0):
        item = self.item_for_path(path)
        return self._index_for_item(item, column) if item else QModelIndex()

    def index(self, row, column, parent=QModelIndex()):
        parent_item = parent.internalPointer() if parent.isValid() else self.root
        if row < 0 or row >= len(parent_item.children):
            return QModelIndex()
        return self.createIndex(row, column, parent_item.children[row])

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        parent_item = index.internalPointer().parent
        if not parent_item or parent_item is self.root:
            return QModelIndex()
        grandparent = parent_item.parent or self.root
        return self.createIndex(grandparent.children.index(parent_item), 0, parent_item)

    def rowCount(self, parent=QModelIndex()):
        item = parent.internalPointer() if parent.isValid() else self.root
        return len(item.children)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            return item.name if index.column() == 0 else item.type_name
        if role == Qt.ItemDataRole.ToolTipRole:
            return item.path
        if role == Qt.ItemDataRole.UserRole:
            return item.path
        if role == Qt.ItemDataRole.UserRole + 1:
            return item.type_name
        if role == Qt.ItemDataRole.UserRole + 2:
            return self.is_hidden(item.path)
        if role == Qt.ItemDataRole.UserRole + 3:
            return self.is_effectively_hidden(item.path)
        if role == Qt.ItemDataRole.UserRole + 4:
            return self.is_hidden_by_ancestor(item.path)
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return None

    def _append_prim(self, prim, parent):
        item = PrimTreeItem(prim, parent)
        parent.children.append(item)
        self.items[item.path] = item
        for child in prim.GetChildren():
            self._append_prim(child, item)

    def _index_for_item(self, item, column):
        if not item or not item.parent:
            return QModelIndex()
        return self.createIndex(item.parent.children.index(item), column, item)

    def _emit_all_rows_changed(self):
        for item in self.items.values():
            left = self._index_for_item(item, 0)
            right = self._index_for_item(item, self.columnCount() - 1)
            if left.isValid():
                self.dataChanged.emit(left, right, [
                    Qt.ItemDataRole.UserRole + 2,
                    Qt.ItemDataRole.UserRole + 3,
                    Qt.ItemDataRole.UserRole + 4,
                ])
