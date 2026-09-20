from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QWidget


class SemanticComparisonToolbar(QWidget):
    filters_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 4)
        self.impact_combo = QComboBox()
        self.domain_combo = QComboBox()
        self.kind_combo = QComboBox()
        self.regressions_only = QCheckBox("Regressions only")
        self.impact_combo.addItem("All impacts")
        self.domain_combo.addItem("All domains")
        self.kind_combo.addItem("All kinds")
        layout.addWidget(QLabel("Impact"))
        layout.addWidget(self.impact_combo)
        layout.addWidget(QLabel("Domain"))
        layout.addWidget(self.domain_combo)
        layout.addWidget(QLabel("Kind"))
        layout.addWidget(self.kind_combo)
        layout.addWidget(self.regressions_only)
        layout.addStretch()
        self.impact_combo.currentIndexChanged.connect(self._emit_filters_changed)
        self.domain_combo.currentIndexChanged.connect(self._emit_filters_changed)
        self.kind_combo.currentIndexChanged.connect(self._emit_filters_changed)
        self.regressions_only.toggled.connect(self._emit_filters_changed)

    def set_comparison(self, comparison):
        selected = self.filters()
        impacts = sorted({change.impact.value for change in comparison.changes})
        domains = sorted({change.domain or change.category for change in comparison.changes})
        kinds = sorted({change.kind.value for change in comparison.changes})
        self._set_items(self.impact_combo, "All impacts", impacts, selected["impact"])
        self._set_items(self.domain_combo, "All domains", domains, selected["domain"])
        self._set_items(self.kind_combo, "All kinds", kinds, selected["kind"])

    def filters(self):
        return {
            "impact": self.impact_combo.currentData() or "",
            "domain": self.domain_combo.currentData() or "",
            "kind": self.kind_combo.currentData() or "",
            "regressions_only": self.regressions_only.isChecked(),
        }

    def _emit_filters_changed(self, *args):
        self.filters_changed.emit()

    @staticmethod
    def _set_items(combo, all_label, values, selected):
        combo.blockSignals(True)
        combo.clear()
        combo.addItem(all_label, "")
        for value in values:
            combo.addItem(value.title(), value)
        index = combo.findData(selected)
        combo.setCurrentIndex(max(0, index))
        combo.blockSignals(False)
