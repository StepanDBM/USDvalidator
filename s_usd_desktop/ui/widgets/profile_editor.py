# ui/profile_editor.py

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from s_usd_desktop.ui.dialogs import CheckPickerDialog, OverridePickerDialog
from s_usd_desktop.ui.menus.check_context_menu import CheckContextMenu
from s_usd_desktop.ui.menus.override_context_menu import OverrideContextMenu
from s_usd_desktop.ui.models.profile_draft import ProfileDraft
from s_usd_core.validation.config_fields import get_config_fields, get_fields_for_check
from s_usd_core.validation.profiles import ValidationProfile
from s_usd_core.validation.rule_config import ValidationRuleConfig

from .collapsible_panel import CollapsiblePanel
from .vertical_resize_handle import VerticalResizeHandle


__all__ = ["ProfileDraft", "ProfileEditor"]


class ProfileEditor(QWidget):
    profiles_changed = Signal()

    def __init__(self, profile_loader, registry, parent=None):
        super().__init__(parent)
        self.profile_loader = profile_loader
        self.registry = registry
        self.definitions = tuple(registry.all())
        self.definition_by_id = {
            definition.check_id: definition for definition in self.definitions
        }
        self.rule_config = ValidationRuleConfig()
        self.current_profile_name = None
        self.draft = None
        self._build_ui()
        self._connect_signals()
        self._populate_filters()
        self._load_profile_list()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_profile_panel())
        splitter.addWidget(self._build_editor_panel())
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([230, 900])
        layout.addWidget(splitter)

    def _build_profile_panel(self):
        widget = QWidget()
        widget.setMinimumWidth(200)
        widget.setMaximumWidth(320)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(QLabel("Profiles"))

        buttons = QHBoxLayout()
        self.new_button = QPushButton("New")
        self.delete_button = QPushButton("Delete")
        buttons.addWidget(self.new_button)
        buttons.addWidget(self.delete_button)
        layout.addLayout(buttons)

        self.profile_list = QListWidget()
        layout.addWidget(self.profile_list, 1)
        return widget

    def _build_editor_panel(self):
        widget = QWidget()

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(6)

        self.editor_scroll_area = QScrollArea()
        self.editor_scroll_area.setWidgetResizable(True)
        self.editor_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.editor_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.editor_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.editor_scroll_content = QWidget()

        content_layout = QVBoxLayout(self.editor_scroll_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(6)

        self.profile_details_panel = CollapsiblePanel("Profile Details",
            self._build_profile_details(), expanded=True,
        )

        self.check_filters_panel = CollapsiblePanel("Check Filters",
            self._build_check_filters(), expanded=False,
        )

        self.profile_checks_panel = CollapsiblePanel("Profile Checks",
            self._build_profile_checks(), expanded=True,
        )

        self.profile_overrides_panel = CollapsiblePanel("Profile Overrides",
            self._build_profile_overrides(), expanded=False,
        )

        content_layout.addWidget(self.profile_details_panel)
        content_layout.addWidget(self.check_filters_panel)
        content_layout.addWidget(self.profile_checks_panel)
        content_layout.addWidget(self.profile_overrides_panel)
        content_layout.addStretch()

        self.editor_scroll_area.setWidget(self.editor_scroll_content)

        layout.addWidget(self.editor_scroll_area, 1)

        actions = QHBoxLayout()
        actions.addStretch()

        self.reset_button = QPushButton("Reset")
        self.save_button = QPushButton("Save")

        actions.addWidget(self.reset_button)
        actions.addWidget(self.save_button)

        layout.addLayout(actions)

        return widget

    def _build_profile_details(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setContentsMargins(8, 4, 8, 8)
        self.name_edit = QLineEdit()
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Description:", self.description_edit)
        return widget

    def _build_check_filters(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 8)
        self.category_combo = QComboBox()
        self.tag_combo = QComboBox()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search profile checks...")
        layout.addWidget(QLabel("Category"))
        layout.addWidget(self.category_combo)
        layout.addWidget(QLabel("Tag"))
        layout.addWidget(self.tag_combo)
        layout.addWidget(self.search_edit, 1)
        return widget

    def _build_profile_checks(self):
        widget = QWidget()

        widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 8)
        layout.setSpacing(4)

        actions = QHBoxLayout()

        self.add_checks_button = QPushButton("Add Checks")

        self.remove_checks_button = QPushButton("Remove Selected")

        actions.addWidget(self.add_checks_button)
        actions.addWidget(self.remove_checks_button)
        actions.addStretch()

        layout.addLayout(actions)

        self.check_tree = QTreeWidget()
        self.check_tree.setHeaderLabels(
            [
                "Check",
                "ID",
                "Phase",
                "Tags",
            ]
        )

        self.check_tree.setColumnWidth(0, 260)
        self.check_tree.setColumnWidth(1, 250)
        self.check_tree.setColumnWidth(2, 100)

        self.check_tree.setMinimumHeight(180)

        self.check_tree.setFixedHeight(340)

        self.check_tree.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self.check_tree.setSelectionMode(
            QAbstractItemView
            .SelectionMode
            .ExtendedSelection
        )

        self.check_tree.setContextMenuPolicy(
            Qt.ContextMenuPolicy
            .CustomContextMenu
        )

        layout.addWidget(self.check_tree)

        self.check_tree_resize_handle = VerticalResizeHandle()

        self.check_tree_resize_handle.resize_requested.connect(
            lambda delta: self._resize_tree(
                self.check_tree,
                self.profile_checks_panel,
                delta,
                180)
)

        layout.addWidget(self.check_tree_resize_handle)

        return widget

    def _build_profile_overrides(self):
        widget = QWidget()

        widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 8)
        layout.setSpacing(4)

        actions = QHBoxLayout()

        self.create_override_button = QPushButton("Create Override")
        self.edit_override_button = QPushButton("Edit Override")
        self.toggle_override_button = QPushButton("Enable / Disable")
        self.remove_override_button = QPushButton("Remove Override")

        actions.addWidget(self.create_override_button)
        actions.addWidget(self.edit_override_button)
        actions.addWidget(self.toggle_override_button)
        actions.addWidget(self.remove_override_button)
        actions.addStretch()

        layout.addLayout(actions)

        self.override_tree = QTreeWidget()

        self.override_tree.setHeaderLabels(
            [
                "Path",
                "Value",
                "State",
                "Related Checks",
            ]
        )

        self.override_tree.setColumnWidth(0, 260)
        self.override_tree.setColumnWidth(1, 140)
        self.override_tree.setColumnWidth(2, 90)

        self.override_tree.setMinimumHeight(140)

        self.override_tree.setFixedHeight(220)

        self.override_tree.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self.override_tree.setContextMenuPolicy(
            Qt.ContextMenuPolicy
            .CustomContextMenu
        )

        layout.addWidget(self.override_tree)
        self.override_tree_resize_handle = VerticalResizeHandle()
        self.override_tree_resize_handle.resize_requested.connect(
            lambda delta: self._resize_tree(
                self.override_tree,
                self.profile_overrides_panel,
                delta,
                140)
)
        layout.addWidget(self.override_tree_resize_handle)

        return widget

    def _connect_signals(self):
        self.profile_list.currentItemChanged.connect(self._on_profile_selected)
        self.new_button.clicked.connect(self._new_profile)
        self.delete_button.clicked.connect(self._delete_profile)
        self.add_checks_button.clicked.connect(self._add_checks)
        self.remove_checks_button.clicked.connect(self._remove_selected_checks)
        self.create_override_button.clicked.connect(self._create_override)
        self.edit_override_button.clicked.connect(self._edit_selected_override)
        self.toggle_override_button.clicked.connect(self._toggle_selected_override)
        self.remove_override_button.clicked.connect(self._remove_selected_override)
        self.override_tree.itemDoubleClicked.connect(self._edit_override_item)
        self.check_tree.customContextMenuRequested.connect(self._show_check_context_menu)
        self.override_tree.customContextMenuRequested.connect(self._show_override_context_menu)
        self.category_combo.currentTextChanged.connect(self._refresh_check_tree)
        self.tag_combo.currentTextChanged.connect(self._refresh_check_tree)
        self.search_edit.textChanged.connect(self._refresh_check_tree)
        self.save_button.clicked.connect(self._save_profile)
        self.reset_button.clicked.connect(self._reset_profile)

    def _resize_tree(
        self,
        tree,
        panel,
        delta,
        minimum_height,
    ):
        new_height = max(
            minimum_height,
            tree.height() + delta,
        )

        tree.setFixedHeight(
            new_height
        )

        panel.updateGeometry()
        self.editor_scroll_content.adjustSize()


    def _load_profile_list(self, select_name=None):
        self.profile_list.blockSignals(True)
        self.profile_list.clear()
        names = list(self.profile_loader.get_profile_names())
        self.profile_list.addItems(names)
        self.profile_list.blockSignals(False)

        if not names:
            self._clear_editor()
            return

        self.profile_list.setCurrentRow(
            names.index(select_name) if select_name in names else 0
        )

    def _on_profile_selected(self, current, previous):
        if current is None:
            return

        self.current_profile_name = current.text()
        profile = self.profile_loader.get_profile(self.current_profile_name)
        self.draft = ProfileDraft.from_profile(profile)
        self._load_draft_into_editor()

    def _load_draft_into_editor(self):
        if self.draft is None:
            return

        self.name_edit.setText(self.draft.name)
        self.description_edit.setPlainText(self.draft.description)
        self._refresh_check_tree()
        self._refresh_override_tree()

    def _clear_editor(self):
        self.current_profile_name = None
        self.draft = None
        self.name_edit.clear()
        self.description_edit.clear()
        self.check_tree.clear()
        self.override_tree.clear()

    def _materialize_check_membership(self):
        if self.draft is None or not self.draft.include_all_checks:
            return

        self.draft.enabled_check_ids = {
            definition.check_id
            for definition in self.definitions
            if definition.enabled
            and definition.check_id not in self.draft.disabled_check_ids
        }
        self.draft.disabled_check_ids.clear()
        self.draft.include_all_checks = False

    def _populate_filters(self):
        categories = sorted(
            {item.category for item in self.definitions if item.category}
        )
        tags = sorted({tag for item in self.definitions for tag in item.tags})
        self.category_combo.blockSignals(True)
        self.tag_combo.blockSignals(True)
        self.category_combo.clear()
        self.tag_combo.clear()
        self.category_combo.addItem("All Categories")
        self.category_combo.addItems(categories)
        self.tag_combo.addItem("All Tags")
        self.tag_combo.addItems(tags)
        self.category_combo.blockSignals(False)
        self.tag_combo.blockSignals(False)

    def _profile_definitions(self):
        if self.draft is None:
            return ()

        if self.draft.include_all_checks:
            return tuple(
                definition
                for definition in self.definitions
                if definition.enabled
                and definition.check_id not in self.draft.disabled_check_ids
            )

        return tuple(
            definition
            for definition in self.definitions
            if definition.check_id in self.draft.enabled_check_ids
        )

    def _refresh_check_tree(self):
        if self.draft is None:
            self.check_tree.clear()
            return

        selected_ids = self._selected_check_ids()
        category_filter = self.category_combo.currentText()
        tag_filter = self.tag_combo.currentText()
        search = self.search_edit.text().strip().lower()
        grouped = {}

        for definition in self._profile_definitions():
            if category_filter != "All Categories" and definition.category != category_filter:
                continue
            if tag_filter != "All Tags" and tag_filter not in definition.tags:
                continue

            searchable = " ".join([
                definition.check_id,
                definition.label,
                definition.description,
                definition.category,
                definition.phase,
                " ".join(definition.tags),
            ]).lower()

            if search and search not in searchable:
                continue

            grouped.setdefault(
                definition.category or "Uncategorized", []
            ).append(definition)

        self.check_tree.clear()

        for category in sorted(grouped):
            category_item = QTreeWidgetItem([category, "", "", ""])
            category_item.setFirstColumnSpanned(True)
            self.check_tree.addTopLevelItem(category_item)

            for definition in sorted(
                grouped[category], key=lambda item: item.label.lower()
            ):
                item = QTreeWidgetItem([
                    definition.label,
                    definition.check_id,
                    definition.phase,
                    ", ".join(definition.tags),
                ])
                item.setData(0, Qt.ItemDataRole.UserRole, definition.check_id)
                item.setToolTip(0, definition.description)
                category_item.addChild(item)

                if definition.check_id in selected_ids:
                    item.setSelected(True)

            category_item.setExpanded(True)

    def _selected_check_ids(self):
        return {
            item.data(0, Qt.ItemDataRole.UserRole)
            for item in self.check_tree.selectedItems()
            if item.data(0, Qt.ItemDataRole.UserRole)
        }

    def _add_checks(self):
        if self.draft is None:
            return

        self.profile_checks_panel.set_expanded(True)
        current_ids = {
            definition.check_id for definition in self._profile_definitions()
        }
        dialog = CheckPickerDialog(self.definitions, current_ids, self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        selected_ids = dialog.selected_check_ids()

        if not selected_ids:
            return

        self._materialize_check_membership()
        self.draft.add_checks(selected_ids)
        self._refresh_check_tree()

    def _remove_selected_checks(self):
        self._remove_checks(self._selected_check_ids())

    def _remove_checks(self, check_ids):
        if self.draft is None or not check_ids:
            return

        self._materialize_check_membership()
        self.draft.remove_checks(check_ids)
        self._refresh_check_tree()
        self._refresh_override_tree()

    def _show_check_context_menu(self, position):
        if self.draft is None:
            return

        item = self.check_tree.itemAt(position)

        if item is None:
            return

        check_id = item.data(0, Qt.ItemDataRole.UserRole)

        if not check_id:
            return

        self.check_tree.setCurrentItem(item)
        menu = CheckContextMenu(
            fields=get_fields_for_check(check_id),
            get_override=self.draft.get_override,
            create_override=self._create_override_for_field,
            edit_override=self._edit_override_for_field,
            set_override_enabled=self._set_field_override_enabled,
            remove_override=self._remove_override_for_field,
            remove_check=lambda: self._remove_checks({check_id}),
            parent=self,
        )
        menu.exec(self.check_tree.viewport().mapToGlobal(position))

    def _refresh_override_tree(self):
        selected_path = self._selected_override_path()
        self.override_tree.clear()

        if self.draft is None:
            return

        field_by_path = {field.path: field for field in get_config_fields()}

        for override in sorted(self.draft.overrides, key=lambda item: item.path):
            field = field_by_path.get(override.path)
            related = []

            if field is not None:
                related = [
                    self.definition_by_id[check_id].label
                    for check_id in field.related_check_ids
                    if check_id in self.definition_by_id
                ]

            item = QTreeWidgetItem([
                override.path,
                str(override.value),
                "Enabled" if override.enabled else "Disabled",
                ", ".join(related),
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, override.path)
            self.override_tree.addTopLevelItem(item)

            if override.path == selected_path:
                self.override_tree.setCurrentItem(item)

    def _selected_override_path(self):
        item = self.override_tree.currentItem()
        return item.data(0, Qt.ItemDataRole.UserRole) if item else None

    def _selected_override(self):
        if self.draft is None:
            return None

        path = self._selected_override_path()
        return self.draft.get_override(path) if path else None

    def _create_override(self):
        self.profile_overrides_panel.set_expanded(True)
        self._open_override_picker(fields=get_config_fields())

    def _edit_selected_override(self):
        override = self._selected_override()

        if override is not None:
            self.profile_overrides_panel.set_expanded(True)
            self._open_override_picker(
                existing_override=override,
                fields=get_config_fields(),
            )

    def _edit_override_item(self, item, column):
        if self.draft is None:
            return

        path = item.data(0, Qt.ItemDataRole.UserRole)
        override = self.draft.get_override(path) if path else None

        if override is not None:
            self._open_override_picker(
                existing_override=override,
                fields=get_config_fields(),
            )

    def _toggle_selected_override(self):
        override = self._selected_override()

        if override is not None:
            self._set_override_enabled(override.path, not override.enabled)

    def _remove_selected_override(self):
        self._remove_override_path(self._selected_override_path())

    def _create_override_for_field(self, field):
        self.profile_overrides_panel.set_expanded(True)
        self._open_override_picker(fields=(field,))

    def _edit_override_for_field(self, field):
        if self.draft is None:
            return

        override = self.draft.get_override(field.path)

        if override is not None:
            self.profile_overrides_panel.set_expanded(True)
            self._open_override_picker(
                existing_override=override,
                fields=(field,),
            )

    def _set_field_override_enabled(self, field, enabled):
        self._set_override_enabled(field.path, enabled)

    def _remove_override_for_field(self, field):
        self._remove_override_path(field.path)

    def _open_override_picker(self, existing_override=None, fields=None):
        if self.draft is None:
            return

        fields = tuple(fields or get_config_fields())

        if not fields:
            QMessageBox.information(
                self,
                "No Configurable Values",
                "No configurable values are available.",
            )
            return

        dialog = OverridePickerDialog(
            fields=fields,
            base_config=self.rule_config,
            definitions=self.definitions,
            profile_check_ids={
                definition.check_id for definition in self._profile_definitions()
            },
            existing_override=existing_override,
            parent=self,
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        override = dialog.selected_override()

        if existing_override and existing_override.path != override.path:
            self.draft.remove_override(existing_override.path)

        self.draft.set_override(
            override.path,
            override.value,
            override.enabled,
        )
        related_ids = dialog.related_check_ids_to_add()

        if related_ids:
            self._materialize_check_membership()
            self.draft.add_checks(related_ids)

        self.profile_overrides_panel.set_expanded(True)
        self._refresh_check_tree()
        self._refresh_override_tree()

    def _set_override_enabled(self, path, enabled):
        if self.draft is None or not path:
            return

        self.draft.set_override_enabled(path, enabled)
        self._refresh_override_tree()

    def _remove_override_path(self, path):
        if self.draft is None or not path:
            return

        self.draft.remove_override(path)
        self._refresh_override_tree()

    def _show_override_context_menu(self, position):
        if self.draft is None:
            return

        item = self.override_tree.itemAt(position)

        if item is None:
            return

        self.override_tree.setCurrentItem(item)
        path = item.data(0, Qt.ItemDataRole.UserRole)
        override = self.draft.get_override(path)

        if override is None:
            return

        menu = OverrideContextMenu(
            override=override,
            edit=lambda: self._open_override_picker(
                existing_override=override,
                fields=get_config_fields(),
            ),
            toggle=lambda: self._set_override_enabled(
                path, not override.enabled
            ),
            remove=lambda: self._remove_override_path(path),
            parent=self,
        )
        menu.exec(self.override_tree.viewport().mapToGlobal(position))

    def _new_profile(self):
        name = "new_profile"
        existing_names = set(self.profile_loader.get_profile_names())
        index = 1

        while name in existing_names:
            name = f"new_profile_{index}"
            index += 1

        self.profile_loader.add_profile(
            ValidationProfile(name=name, include_all_checks=False)
        )
        self.profile_loader.save()
        self._load_profile_list(select_name=name)
        self.profile_details_panel.set_expanded(True)
        self.profiles_changed.emit()

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
            self.profile_loader.delete_profile(name)
            self.profile_loader.save()
        except (KeyError, ValueError) as exc:
            QMessageBox.warning(self, "Cannot Delete Profile", str(exc))
            return

        self._load_profile_list()
        self.profiles_changed.emit()

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

        existing_names = set(self.profile_loader.get_profile_names())

        if name != self.current_profile_name and name in existing_names:
            QMessageBox.warning(
                self,
                "Invalid Profile",
                f"Profile already exists: {name}",
            )
            return

        self.draft.name = name
        self.draft.description = self.description_edit.toPlainText().strip()
        profile = self.draft.to_profile()

        if self.current_profile_name and name != self.current_profile_name:
            self.profile_loader.replace_profile(self.current_profile_name, profile)
        else:
            self.profile_loader.update_profile(profile)

        self.profile_loader.save()
        self.current_profile_name = name
        self._load_profile_list(select_name=name)
        self.profiles_changed.emit()

    def _reset_profile(self):
        if self.current_profile_name is None:
            return

        profile = self.profile_loader.get_profile(self.current_profile_name)
        self.draft = ProfileDraft.from_profile(profile)
        self._load_draft_into_editor()
