from PySide6.QtCore import QSortFilterProxyModel, Qt

from s_usd_core.validation.enums import CheckStatus, Severity


class PrimOutlinerProxy(QSortFilterProxyModel):
    TYPE_ROLE = Qt.ItemDataRole.UserRole + 1
    SUMMARY_ROLE = Qt.ItemDataRole.UserRole + 5
    ANIMATED_ROLE = Qt.ItemDataRole.UserRole + 7
    COMPARISON_ROLE = Qt.ItemDataRole.UserRole + 10
    MATCH_ROLE = Qt.ItemDataRole.UserRole + 20
    NO_MATCH = 0
    DIRECT_MATCH = 1
    ANCESTOR_CONTEXT = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.query = ""
        self.enabled_types = set()
        self.all_types = True
        self.validation_statuses = set()
        self.findings_only = False
        self.animated_only = False
        self.comparison_impacts = set()
        self.comparison_kinds = set()
        self.setRecursiveFilteringEnabled(False)
        self.setAutoAcceptChildRows(False)

    @property
    def filters_active(self):
        return bool(self.query or not self.all_types or self.validation_statuses or self.findings_only or self.animated_only or self.comparison_impacts or self.comparison_kinds)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == self.MATCH_ROLE:
            source_index = self.mapToSource(index)
            if self._matches_index(source_index):
                return self.DIRECT_MATCH
            if self._has_matching_descendant(source_index):
                return self.ANCESTOR_CONTEXT
            return self.NO_MATCH
        if role == Qt.ItemDataRole.ToolTipRole and self.filters_active:
            source_index = self.mapToSource(index)
            if not self._matches_index(source_index):
                count = self._matching_descendant_count(source_index)
                if count:
                    base = super().data(index, role) or source_index.data(role) or ""
                    suffix = f"Shown because {count} descendant{'s' if count != 1 else ''} match the active filters."
                    return f"{base}\n\n{suffix}" if base else suffix
        return super().data(index, role)

    def set_query(self, value):
        self.query = str(value or "").strip().lower()
        self.invalidateFilter()

    def set_type_filter(self, enabled_types, all_types=False):
        self.enabled_types = set(enabled_types or ())
        self.all_types = bool(all_types)
        self.invalidateFilter()

    def set_validation_statuses(self, statuses):
        self.validation_statuses = set(statuses or ())
        self.invalidateFilter()

    def set_findings_only(self, enabled):
        self.findings_only = bool(enabled)
        self.invalidateFilter()

    def set_animated_only(self, enabled):
        self.animated_only = bool(enabled)
        self.invalidateFilter()

    def set_comparison_filters(self, impacts=(), kinds=()):
        self.comparison_impacts = set(impacts or ())
        self.comparison_kinds = set(kinds or ())
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(source_row, 0, source_parent)
        return self._matches_index(index) or self._has_matching_descendant(index)

    def _matches_index(self, index):
        if not index.isValid():
            return False
        node = index.internalPointer()
        prim = node.prim
        values = (prim.GetName(), prim.GetPath().pathString, prim.GetTypeName() or "typeless")
        if self.query and not any(self.query in value.lower() for value in values):
            return False
        if not self.all_types and index.data(self.TYPE_ROLE) not in self.enabled_types:
            return False
        summary = index.data(self.SUMMARY_ROLE)
        direct = summary.direct_evidence if summary else ()
        if self.findings_only and not direct:
            return False
        if self.validation_statuses and not self._matches_validation(direct):
            return False
        if self.animated_only and not index.data(self.ANIMATED_ROLE):
            return False
        comparison = index.data(self.COMPARISON_ROLE)
        direct_changes = comparison.direct_changes if comparison else ()
        if self.comparison_impacts and not any(change.impact.value in self.comparison_impacts for change in direct_changes):
            return False
        if self.comparison_kinds and not any(change.kind.value in self.comparison_kinds for change in direct_changes):
            return False
        return True

    def _has_matching_descendant(self, index):
        model = self.sourceModel()
        for row in range(model.rowCount(index)):
            child = model.index(row, 0, index)
            if self._matches_index(child) or self._has_matching_descendant(child):
                return True
        return False

    def _matching_descendant_count(self, index):
        model = self.sourceModel()
        count = 0
        for row in range(model.rowCount(index)):
            child = model.index(row, 0, index)
            count += int(self._matches_index(child)) + self._matching_descendant_count(child)
        return count

    def _matches_validation(self, evidence):
        if not evidence:
            return "NONE" in self.validation_statuses
        matches = set()
        statuses = {item.status for item in evidence}
        if statuses == {CheckStatus.PASSED}:
            matches.add("PASSED")
        if CheckStatus.ERROR in statuses:
            matches.add("ERROR")
        if CheckStatus.SKIPPED in statuses:
            matches.add("SKIPPED")
        for item in evidence:
            if item.severity is Severity.INFO:
                matches.add("INFO")
            if item.status is not CheckStatus.FAILED:
                continue
            if item.severity is Severity.ERROR:
                matches.add("FAILED")
            elif item.severity is Severity.WARNING:
                matches.add("WARNING")
        return bool(matches & self.validation_statuses)
