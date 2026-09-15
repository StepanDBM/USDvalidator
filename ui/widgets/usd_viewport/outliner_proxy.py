from PySide6.QtCore import QSortFilterProxyModel


class PrimOutlinerProxy(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.query = ""
        self.setRecursiveFilteringEnabled(True)
        self.setAutoAcceptChildRows(True)

    def set_query(self, value):
        self.query = str(value or "").strip().lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self.query:
            return True
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)
        node = index.internalPointer()
        prim = node.prim
        values = (prim.GetName(), prim.GetPath().pathString, prim.GetTypeName() or "typeless")
        return any(self.query in value.lower() for value in values)
