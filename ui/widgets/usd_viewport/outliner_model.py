from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, Signal

from .prim_finding_index import PrimFindingIndex


@dataclass
class PrimTreeItem:
    prim: object = None
    parent: "PrimTreeItem | None" = None
    children: list["PrimTreeItem"] = field(default_factory=list)
    validation_summary: object = None
    validation_visible: bool = False
    animated: bool = False

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
        self.findings = PrimFindingIndex()
        self.validation_visible = False
        
    def set_validation_results(self, results):
        self.findings = PrimFindingIndex(self.stage, results)

        for item in self.items.values():
            item.validation_summary = self.findings.summary(item.path)
            item.validation_visible = self.validation_visible

        self._emit_all_rows_changed()


    def set_validation_visible(self, visible):
        self.validation_visible = bool(visible)

        for item in self.items.values():
            item.validation_visible = self.validation_visible

        self._emit_all_rows_changed()


    def validation_results_for_paths(self, paths, include_descendants=False):
        return self.findings.results_for_paths(
            paths,
            include_descendants=include_descendants,
        )

    def set_stage(self, stage):
        self.beginResetModel()
        self.stage = stage
        self.root = PrimTreeItem()
        self.items = {}
        self.hidden_paths = set()
        if stage:
            for prim in stage.GetPseudoRoot().GetChildren():
                self._append_prim(prim, self.root)

        self.findings = PrimFindingIndex(stage, self.findings.results)

        for item in self.items.values():
            item.validation_summary = self.findings.summary(item.path)
            item.validation_visible = self.validation_visible

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
            summary = item.validation_summary
            return f"{item.path}\n\n{summary.tooltip}" if summary and summary.total_count else item.path
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
        if role == Qt.ItemDataRole.UserRole + 5:
            return item.validation_summary
        if role == Qt.ItemDataRole.UserRole + 6:
            return item.validation_visible
        if role == Qt.ItemDataRole.UserRole + 7:
            return item.animated

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
        item = PrimTreeItem(prim, parent, animated=self._prim_is_animated(prim))
        parent.children.append(item)
        self.items[item.path] = item
        for child in prim.GetChildren():
            self._append_prim(child, item)

    @staticmethod
    def _prim_is_animated(prim):
        for attribute in prim.GetAttributes():
            try:
                if attribute.ValueMightBeTimeVarying() or attribute.GetNumTimeSamples() > 0:
                    return True
            except Exception:
                continue
        return False

    def _index_for_item(self, item, column):
        if not item or not item.parent:
            return QModelIndex()
        return self.createIndex(item.parent.children.index(item), column, item)

    def _emit_all_rows_changed(self):
        for item in self.items.values():
            left = self._index_for_item(item, 0)
            right = self._index_for_item(item, self.columnCount() - 1)

            if not left.isValid():
                continue

            self.dataChanged.emit(left, right, [
                Qt.ItemDataRole.DisplayRole,
                Qt.ItemDataRole.ToolTipRole,
                Qt.ItemDataRole.UserRole + 2,
                Qt.ItemDataRole.UserRole + 3,
                Qt.ItemDataRole.UserRole + 4,
                Qt.ItemDataRole.UserRole + 5,
                Qt.ItemDataRole.UserRole + 6,
                Qt.ItemDataRole.UserRole + 7,
            ])