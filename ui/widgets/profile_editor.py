from dataclasses import dataclass, field

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from validation.models import CheckDefinition
from validation.profiles import ValidationProfile


@dataclass
class ProfileDraft:
    name: str
    description: str
    enabled_check_ids: set[str] = field(default_factory=set)
    disabled_check_ids: set[str] = field(default_factory=set)

    @classmethod
    def from_profile(cls, profile):
        return cls(
            name=profile.name,
            description=profile.description,
            enabled_check_ids=set(
                profile.enabled_check_ids
            ),
            disabled_check_ids=set(
                profile.disabled_check_ids
            ),
        )

    def to_profile(self):
        return ValidationProfile(
            name=self.name.strip(),
            description=self.description.strip(),
            enabled_check_ids=frozenset(
                self.enabled_check_ids
            ),
            disabled_check_ids=frozenset(
                self.disabled_check_ids
            ),
        )


class ProfileEditor(QWidget):
    profiles_changed = Signal()

    def __init__(
        self,
        profile_loader,
        registry,
        parent=None,
    ):
        super().__init__(parent)

        self.profile_loader = profile_loader
        self.registry = registry
        self.definitions = tuple(
            registry.all()
        )

        self._loading_tree = False
        self.current_profile_name = None
        self.draft = None

        self._build_ui()
        self._populate_filters()
        self._load_profile_list()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self):
        main_layout = QVBoxLayout(self)

        splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        splitter.addWidget(
            self._build_profile_panel()
        )

        splitter.addWidget(
            self._build_editor_panel()
        )

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

    def _build_profile_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(
            QLabel("Profiles")
        )

        button_layout = QHBoxLayout()

        self.new_button = QPushButton("New")
        self.delete_button = QPushButton("Delete")

        button_layout.addWidget(
            self.new_button
        )
        button_layout.addWidget(
            self.delete_button
        )

        layout.addLayout(button_layout)

        self.profile_list = QListWidget()
        layout.addWidget(
            self.profile_list,
            1,
        )

        return widget

    def _build_editor_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # --------------------------------------------------------------
        # Profile details
        # --------------------------------------------------------------

        details_group = QGroupBox(
            "Profile Details"
        )

        details_layout = QFormLayout(
            details_group
        )

        self.name_edit = QLineEdit()
        self.description_edit = QTextEdit()

        self.description_edit.setMaximumHeight(
            90
        )

        details_layout.addRow(
            "Name:",
            self.name_edit,
        )

        details_layout.addRow(
            "Description:",
            self.description_edit,
        )

        layout.addWidget(
            details_group
        )

        # --------------------------------------------------------------
        # Filters
        # --------------------------------------------------------------

        filters_group = QGroupBox(
            "Check Filters"
        )

        filters_layout = QHBoxLayout(
            filters_group
        )

        self.category_combo = QComboBox()
        self.tag_combo = QComboBox()
        self.search_edit = QLineEdit()

        self.search_edit.setPlaceholderText(
            "Search checks..."
        )

        filters_layout.addWidget(
            QLabel("Category")
        )
        filters_layout.addWidget(
            self.category_combo
        )

        filters_layout.addWidget(
            QLabel("Tag")
        )
        filters_layout.addWidget(
            self.tag_combo
        )

        filters_layout.addWidget(
            self.search_edit,
            1,
        )

        layout.addWidget(
            filters_group
        )

        # --------------------------------------------------------------
        # Checks
        # --------------------------------------------------------------

        checks_group = QGroupBox(
            "Checks"
        )

        checks_layout = QVBoxLayout(
            checks_group
        )

        self.check_tree = QTreeWidget()
        self.check_tree.setHeaderLabels(
            [
                "Check",
                "ID",
                "Tags",
                "Status",
            ]
        )

        self.check_tree.setColumnWidth(
            0,
            240,
        )

        self.check_tree.setColumnWidth(
            1,
            250,
        )

        self.check_tree.setColumnWidth(
            2,
            180,
        )

        checks_layout.addWidget(
            self.check_tree
        )
        self.check_tree.itemChanged.connect(
            self._on_check_item_changed
        )
        layout.addWidget(
            checks_group,
            1,
        )

        # --------------------------------------------------------------
        # Actions
        # --------------------------------------------------------------

        action_layout = QHBoxLayout()

        action_layout.addStretch()

        self.reset_button = QPushButton(
            "Reset"
        )

        self.save_button = QPushButton(
            "Save"
        )

        action_layout.addWidget(
            self.reset_button
        )

        action_layout.addWidget(
            self.save_button
        )

        layout.addLayout(
            action_layout
        )

        # --------------------------------------------------------------
        # Connections
        # --------------------------------------------------------------

        self.profile_list.currentItemChanged.connect(
            self._on_profile_selected
        )

        self.new_button.clicked.connect(
            self._new_profile
        )

        self.delete_button.clicked.connect(
            self._delete_profile
        )

        self.save_button.clicked.connect(
            self._save_profile
        )

        self.reset_button.clicked.connect(
            self._reset_profile
        )

        self.category_combo.currentTextChanged.connect(
            self._refresh_check_tree
        )

        self.tag_combo.currentTextChanged.connect(
            self._refresh_check_tree
        )

        self.search_edit.textChanged.connect(
            self._refresh_check_tree
        )

        return widget

    def _on_check_item_changed(self, item, column):
        if self._loading_tree:
            return

        if self.draft is None:
            return

        check_id = item.data(
            0,
            Qt.ItemDataRole.UserRole,
        )

        if not check_id:
            return

        definition = next(
            (
                definition
                for definition in self.definitions
                if definition.check_id == check_id
            ),
            None,
        )

        if definition is None:
            return

        state = item.checkState(0)

        if state == Qt.CheckState.Checked:
            if definition.enabled:
                self.draft.disabled_check_ids.discard(
                    check_id
                )
            else:
                self.draft.enabled_check_ids.add(
                    check_id
                )

        else:
            if definition.enabled:
                self.draft.disabled_check_ids.add(
                    check_id
                )
            else:
                self.draft.enabled_check_ids.discard(
                    check_id
                )

        item.setText(
            3,
            self._check_status(definition),
        )

    # ------------------------------------------------------------------
    # Profile list
    # ------------------------------------------------------------------

    def _load_profile_list(self, select_name=None):
        self.profile_list.blockSignals(True)
        self.profile_list.clear()

        names = self.profile_loader.get_profile_names()

        for name in names:
            self.profile_list.addItem(name)

        self.profile_list.blockSignals(False)

        if not names:
            self._clear_editor()
            return

        if select_name in names:
            index = names.index(select_name)
        else:
            index = 0

        self.profile_list.setCurrentRow(index)

    def _on_profile_selected(
        self,
        current,
        previous,
    ):
        if current is None:
            return

        name = current.text()

        profile = self.profile_loader.get_profile(
            name
        )

        self.current_profile_name = name
        self.draft = ProfileDraft.from_profile(
            profile
        )

        self._load_draft_into_editor()

    # ------------------------------------------------------------------
    # Draft/editor state
    # ------------------------------------------------------------------

    def _load_draft_into_editor(self):
        if self.draft is None:
            return

        self.name_edit.setText(
            self.draft.name
        )

        self.description_edit.setPlainText(
            self.draft.description
        )

        self._refresh_check_tree()

    def _clear_editor(self):
        self.current_profile_name = None
        self.draft = None

        self.name_edit.clear()
        self.description_edit.clear()
        self.check_tree.clear()

    # ------------------------------------------------------------------
    # Check filters
    # ------------------------------------------------------------------

    def _populate_filters(self):
        categories = sorted(
            {
                definition.category
                for definition in self.definitions
                if definition.category
            }
        )

        tags = sorted(
            {
                tag
                for definition in self.definitions
                for tag in definition.tags
            }
        )

        self.category_combo.blockSignals(True)
        self.tag_combo.blockSignals(True)

        self.category_combo.clear()
        self.tag_combo.clear()

        self.category_combo.addItem("All")
        self.tag_combo.addItem("All")

        self.category_combo.addItems(
            categories
        )

        self.tag_combo.addItems(
            tags
        )

        self.category_combo.blockSignals(False)
        self.tag_combo.blockSignals(False)

    def _refresh_check_tree(self):
        self._loading_tree = True

        try:
            self.check_tree.clear()

            category_filter = (
                self.category_combo.currentText()
            )

            tag_filter = (
                self.tag_combo.currentText()
            )

            search = (
                self.search_edit.text()
                .strip()
                .lower()
            )

            grouped = {}

            for definition in self.definitions:
                if (
                    category_filter != "All"
                    and definition.category != category_filter
                ):
                    continue

                if (
                    tag_filter != "All"
                    and tag_filter not in definition.tags
                ):
                    continue

                if search:
                    searchable = " ".join(
                        [
                            definition.check_id,
                            definition.label,
                            definition.description,
                            definition.category,
                            " ".join(definition.tags),
                        ]
                    ).lower()

                    if search not in searchable:
                        continue

                grouped.setdefault(
                    definition.category or "Uncategorized",
                    [],
                ).append(definition)

            for category in sorted(grouped):
                category_item = QTreeWidgetItem(
                    [
                        category,
                        "",
                        "",
                        "",
                    ]
                )

                category_item.setFlags(
                    category_item.flags()
                    & ~Qt.ItemFlag.ItemIsUserCheckable
                )

                self.check_tree.addTopLevelItem(
                    category_item
                )

                for definition in sorted(
                    grouped[category],
                    key=lambda item: item.label.lower(),
                ):
                    item = QTreeWidgetItem(
                        [
                            definition.label,
                            definition.check_id,
                            ", ".join(definition.tags),
                            self._check_status(definition),
                        ]
                    )

                    item.setData(
                        0,
                        Qt.ItemDataRole.UserRole,
                        definition.check_id,
                    )

                    item.setFlags(
                        item.flags()
                        | Qt.ItemFlag.ItemIsUserCheckable
                    )

                    item.setCheckState(
                        0,
                        self._check_state(definition),
                    )

                    category_item.addChild(item)

                category_item.setExpanded(True)

        finally:
            self._loading_tree = False

    # ------------------------------------------------------------------
    # Check state
    # ------------------------------------------------------------------

    def _check_state(self, definition):
        if self.draft is None:
            return Qt.CheckState.Unchecked

        check_id = definition.check_id

        if check_id in self.draft.disabled_check_ids:
            return Qt.CheckState.Unchecked

        if check_id in self.draft.enabled_check_ids:
            return Qt.CheckState.Checked

        # No explicit override:
        # inherit the definition's default state.
        if definition.enabled:
            return Qt.CheckState.Checked

        return Qt.CheckState.Unchecked

    def _check_status(self, definition):
        if self.draft is None:
            return "Inherited"

        check_id = definition.check_id

        if check_id in self.draft.enabled_check_ids:
            return "Enabled override"

        if check_id in self.draft.disabled_check_ids:
            return "Disabled override"

        return (
            "Enabled"
            if definition.enabled
            else "Disabled"
        )

    # ------------------------------------------------------------------
    # New
    # ------------------------------------------------------------------

    def _new_profile(self):
        name = "new_profile"

        existing_names = set(
            self.profile_loader.get_profile_names()
        )

        index = 1

        while name in existing_names:
            name = f"new_profile_{index}"
            index += 1

        profile = ValidationProfile(
            name=name,
            description="",
        )

        self.profile_loader.add_profile(
            profile
        )

        self._load_profile_list(
            select_name=name
        )

        self.profiles_changed.emit()

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def _delete_profile(self):
        item = self.profile_list.currentItem()

        if item is None:
            return

        name = item.text()

        answer = QMessageBox.question(
            self,
            "Delete Profile",
            f"Delete profile '{name}'?",
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            self.profile_loader.delete_profile(
                name
            )

        except (KeyError, ValueError) as exc:
            QMessageBox.warning(
                self,
                "Cannot Delete Profile",
                str(exc),
            )
            return

        self._load_profile_list()

        self.profiles_changed.emit()

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def _save_profile(self):
        if self.draft is None:
            return

        name = self.name_edit.text().strip()

        if not name:
            QMessageBox.warning(
                self,
                "Invalid Profile",
                "Profile name cannot be empty.",
            )
            return

        existing_names = set(
            self.profile_loader.get_profile_names()
        )

        if (
            name != self.current_profile_name
            and name in existing_names
        ):
            QMessageBox.warning(
                self,
                "Invalid Profile",
                f"Profile already exists: {name}",
            )
            return

        self.draft.name = name
        self.draft.description = (
            self.description_edit
            .toPlainText()
            .strip()
        )

        profile = self.draft.to_profile()

        if (
            self.current_profile_name
            and name != self.current_profile_name
        ):
            self.profile_loader.replace_profile(
                self.current_profile_name,
                profile,
            )
        else:
            self.profile_loader.update_profile(
                profile
            )

        self.profile_loader.save()

        self.current_profile_name = name

        self._load_profile_list(
            select_name=name
        )

        self.profiles_changed.emit()

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def _reset_profile(self):
        if self.current_profile_name is None:
            return

        profile = self.profile_loader.get_profile(
            self.current_profile_name
        )

        self.draft = ProfileDraft.from_profile(
            profile
        )

        self._load_draft_into_editor()