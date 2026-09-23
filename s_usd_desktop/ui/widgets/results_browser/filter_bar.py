from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QWidget


from s_usd_desktop.ui.tooltips import TooltipText


class ResultsFilterBar(QWidget):
    filters_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.status_combo = QComboBox()
        self.severity_combo = QComboBox()
        self.category_combo = QComboBox()
        self.search_edit = QLineEdit()
        self.status_combo.setToolTip(TooltipText.RESULT_FILTER_STATUS)
        self.severity_combo.setToolTip(TooltipText.RESULT_FILTER_SEVERITY)
        self.category_combo.setToolTip(TooltipText.RESULT_FILTER_CATEGORY)
        self.search_edit.setToolTip(TooltipText.RESULT_FILTER_SEARCH)
        self.search_edit.setPlaceholderText(
            "Search check IDs, labels, messages, locations or suggestions..."
        )
        self.status_combo.addItems(
            ["All Statuses", "PASSED", "FAILED", "SKIPPED", "ERROR"]
        )
        self.severity_combo.addItems(
            ["All Severities", "ERROR", "WARNING", "INFO"]
        )
        self.category_combo.addItem("All Categories")
        layout.addWidget(QLabel("Status"))
        layout.addWidget(self.status_combo)
        layout.addWidget(QLabel("Severity"))
        layout.addWidget(self.severity_combo)
        layout.addWidget(QLabel("Category"))
        layout.addWidget(self.category_combo)
        layout.addWidget(self.search_edit, 1)
        self.status_combo.currentTextChanged.connect(self.filters_changed)
        self.severity_combo.currentTextChanged.connect(self.filters_changed)
        self.category_combo.currentTextChanged.connect(self.filters_changed)
        self.search_edit.textChanged.connect(self.filters_changed)

    def set_categories(self, categories):
        current = self.category_combo.currentText()
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItems(["All Categories", *sorted(categories)])
        index = self.category_combo.findText(current)
        self.category_combo.setCurrentIndex(max(0, index))
        self.category_combo.blockSignals(False)

    def values(self):
        return {
            "status": self.status_combo.currentText(),
            "severity": self.severity_combo.currentText(),
            "category": self.category_combo.currentText(),
            "search": self.search_edit.text().strip().lower(),
        }

    def reset(self):
        self.status_combo.setCurrentIndex(0)
        self.severity_combo.setCurrentIndex(0)
        self.category_combo.setCurrentIndex(0)
        self.search_edit.clear()
