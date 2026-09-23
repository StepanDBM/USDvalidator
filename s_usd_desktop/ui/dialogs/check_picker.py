from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)


from s_usd_desktop.ui.tooltips import TooltipText


class CheckPickerDialog(QDialog):
    def __init__(self, definitions, excluded_ids=(), parent=None):
        super().__init__(parent)
        self.definitions = tuple(definitions)
        self.excluded_ids = set(excluded_ids)
        self.setWindowTitle("Add Checks")
        self.resize(900, 560)
        self._build_ui()
        self._populate_filters()
        self._refresh_tree()

    def selected_check_ids(self):
        selected = []
        root = self.check_tree.invisibleRootItem()

        for category_index in range(root.childCount()):
            category_item = root.child(category_index)

            for check_index in range(category_item.childCount()):
                item = category_item.child(check_index)

                if item.checkState(0) == Qt.CheckState.Checked:
                    selected.append(item.data(0, Qt.ItemDataRole.UserRole))

        return tuple(selected)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Add Registered Checks")
        help_label = QLabel(
            "Select checks implemented in Python and add them to this profile."
        )
        help_label.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(help_label)

        filters = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setToolTip(TooltipText.CHECK_PICKER_SEARCH)
        self.search_edit.setPlaceholderText("Search checks, IDs or descriptions...")
        self.category_combo = QComboBox()
        self.category_combo.setToolTip(TooltipText.CHECK_PICKER_CATEGORY)
        self.phase_combo = QComboBox()
        self.phase_combo.setToolTip(TooltipText.CHECK_PICKER_PHASE)
        self.tag_combo = QComboBox()
        self.tag_combo.setToolTip(TooltipText.CHECK_PICKER_TAG)
        filters.addWidget(QLabel("Category"))
        filters.addWidget(self.category_combo)
        filters.addWidget(QLabel("Phase"))
        filters.addWidget(self.phase_combo)
        filters.addWidget(QLabel("Tag"))
        filters.addWidget(self.tag_combo)
        filters.addWidget(self.search_edit, 1)
        layout.addLayout(filters)

        self.check_tree = QTreeWidget()
        self.check_tree.setToolTip(TooltipText.PROFILE_CHECK_LIST)
        self.check_tree.setHeaderLabels(
            ["Check", "ID", "Phase", "Target", "Severity", "Tags"]
        )
        self.check_tree.setColumnWidth(0, 260)
        self.check_tree.setColumnWidth(1, 250)
        self.check_tree.setColumnWidth(2, 100)
        self.check_tree.setColumnWidth(3, 150)
        layout.addWidget(self.check_tree, 1)

        self.selection_label = QLabel("Selected: 0")
        layout.addWidget(self.selection_label)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Ok
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Add Selected")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.search_edit.textChanged.connect(self._refresh_tree)
        self.category_combo.currentTextChanged.connect(self._refresh_tree)
        self.phase_combo.currentTextChanged.connect(self._refresh_tree)
        self.tag_combo.currentTextChanged.connect(self._refresh_tree)
        self.check_tree.itemChanged.connect(self._update_selection_count)

    def _populate_filters(self):
        available = [
            item for item in self.definitions
            if item.check_id not in self.excluded_ids
        ]
        self.category_combo.addItems(
            ["All Categories"]
            + sorted({item.category for item in available if item.category})
        )
        self.phase_combo.addItems(
            ["All Phases"]
            + sorted({item.phase for item in available if item.phase})
        )
        self.tag_combo.addItems(
            ["All Tags"]
            + sorted({tag for item in available for tag in item.tags})
        )

    def _refresh_tree(self):
        search = self.search_edit.text().strip().lower()
        category = self.category_combo.currentText()
        phase = self.phase_combo.currentText()
        tag = self.tag_combo.currentText()
        self.check_tree.blockSignals(True)
        self.check_tree.clear()
        grouped = {}

        for definition in self.definitions:
            if definition.check_id in self.excluded_ids:
                continue
            searchable = " ".join(
                [definition.label, definition.check_id, definition.description, *definition.tags]
            ).lower()

            if search and search not in searchable:
                continue
            if category != "All Categories" and definition.category != category:
                continue
            if phase != "All Phases" and definition.phase != phase:
                continue
            if tag != "All Tags" and tag not in definition.tags:
                continue

            grouped.setdefault(definition.category or "Uncategorized", []).append(definition)

        for category_name in sorted(grouped):
            category_item = QTreeWidgetItem([category_name])
            self.check_tree.addTopLevelItem(category_item)

            for definition in sorted(grouped[category_name], key=lambda item: item.label.lower()):
                item = QTreeWidgetItem([
                    definition.label,
                    definition.check_id,
                    definition.phase,
                    definition.target_type.__name__,
                    definition.default_severity.value,
                    ", ".join(definition.tags),
                ])
                item.setData(0, Qt.ItemDataRole.UserRole, definition.check_id)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(0, Qt.CheckState.Unchecked)
                item.setToolTip(
                    0,
                    f"{TooltipText.PROFILE_CHECK_ROW}\n\n"
                    f"Check: {definition.label}\n"
                    f"ID: {definition.check_id}\n"
                    f"Description: {definition.description}\n"
                    f"Phase: {definition.phase}\n"
                    f"Severity: {definition.default_severity.value}"
                )
                category_item.addChild(item)

            category_item.setExpanded(True)

        self.check_tree.blockSignals(False)
        self._update_selection_count()

    def _update_selection_count(self, item=None, column=0):
        self.selection_label.setText(f"Selected: {len(self.selected_check_ids())}")
