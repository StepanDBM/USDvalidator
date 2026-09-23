from __future__ import annotations

from PySide6.QtCore import QItemSelectionModel, Qt, Signal
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QMenu,
    QPushButton,
    QToolButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from s_usd_desktop.ui.tooltips import TooltipText

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
    validation_toggled = Signal(bool)
    validation_refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.primary_path = ""
        self._expansion_before_filter = None
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Search prim name, path or type...")
        self.tree = QTreeView()
        self.tree.setAlternatingRowColors(True)
        self.tree.setUniformRowHeights(True)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.validation_toggle = QToolButton()
        self.validation_toggle.setText("Validation")
        self.validation_toggle.setCheckable(True)
        self.validation_toggle.setToolTip("Show validation badges for the loaded source")

        self.validation_refresh = QPushButton("Refresh")
        self.validation_refresh.setToolTip("Run validation again for the loaded source")
        self.validation_refresh.setEnabled(False)

        self.type_filter = QToolButton()
        self.type_filter.setText("Types: All")
        self.type_filter.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.type_menu = QMenu(self.type_filter)
        self.type_filter.setMenu(self.type_menu)
        self.type_actions = {}

        self.status_filter = QToolButton()
        self.status_filter.setText("Status: All")
        self.status_filter.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.status_menu = QMenu(self.status_filter)
        self.status_filter.setMenu(self.status_menu)
        self.status_actions = {}
        for key, label in (("PASSED", "Passed"), ("FAILED", "Failed"), ("ERROR", "Errors"), ("WARNING", "Warnings"), ("INFO", "Information"), ("SKIPPED", "Skipped"), ("NONE", "No findings")):
            action = self.status_menu.addAction(label)
            action.setCheckable(True)
            action.toggled.connect(self._status_filter_changed)
            self.status_actions[key] = action

        self.findings_only = QCheckBox("Findings only")
        self.animated_only = QCheckBox("Animated only")
        self.filter_edit.setToolTip(
            "Filter the stage hierarchy by prim name, path, or type without modifying the stage."
        )
        self.tree.setToolTip(TooltipText.VIEWPORT_OUTLINER)
        self.validation_toggle.setToolTip(TooltipText.VIEWPORT_VALIDATION_CONTEXT)
        self.validation_refresh.setToolTip(
            "Run validation again for the loaded source and refresh validation badges in the outliner."
        )
        self.type_filter.setToolTip(
            "Show only prims whose USD type matches the selected type filters."
        )
        self.status_filter.setToolTip(
            "Show only prims matching selected validation states, such as failures or warnings."
        )
        self.findings_only.setToolTip(
            "Hide prims without validation or comparison findings while preserving their required ancestors."
        )
        self.animated_only.setToolTip(
            "Show prims containing time-varying properties while preserving their hierarchy ancestors."
        )
        self.display_mode = QComboBox()
        self.display_mode.addItems(("All", "Validation", "Comparison", "Animation"))
        self.display_mode.setToolTip("Choose visible outliner evidence layers")
        self.comparison_filter = QToolButton()
        self.display_mode.setToolTip(
            "Choose how outliner rows are labeled, such as prim name, full path, or type-aware display."
        )
        self.comparison_filter.setToolTip(TooltipText.VIEWPORT_COMPARISON_CONTEXT)
        self.comparison_filter.setText("Comparison: All")
        self.comparison_filter.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.comparison_menu = QMenu(self.comparison_filter)
        self.comparison_filter.setMenu(self.comparison_menu)
        self.comparison_actions = {}
        for group, values in (("Impact", ("INFORMATIONAL", "LOW", "MEDIUM", "HIGH", "CRITICAL")), ("Kind", ("ADDED", "REMOVED", "CHANGED", "INCREASED", "DECREASED", "REGRESSION", "RESOLVED", "UNCHANGED"))):
            submenu = self.comparison_menu.addMenu(group)
            for value in values:
                action = submenu.addAction(value.title())
                action.setCheckable(True)
                action.toggled.connect(self._comparison_filter_changed)
                self.comparison_actions[(group, value)] = action

        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.addWidget(self.filter_edit, 1)
        filter_layout.addWidget(self.validation_toggle)
        filter_layout.addWidget(self.validation_refresh)

        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.addWidget(self.type_filter)
        options_layout.addWidget(self.status_filter)
        options_layout.addWidget(self.findings_only)
        options_layout.addWidget(self.animated_only)
        options_layout.addWidget(self.comparison_filter)
        options_layout.addWidget(self.display_mode)
        options_layout.addStretch(1)

        self.model = PrimOutlinerModel(self)
        self.proxy = PrimOutlinerProxy(self)
        self.proxy.setSourceModel(self.model)
        self.tree.setModel(self.proxy)
        self.tree.setItemDelegate(PrimRowDelegate(self.tree))
        self.tree.setColumnWidth(0, 240)
        self.tree.setColumnWidth(1, 100)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(filter_layout)
        layout.addLayout(options_layout)
        layout.addWidget(self.tree, 1)

        self.validation_toggle.toggled.connect(self._validation_toggled)
        self.validation_refresh.clicked.connect(self.validation_refresh_requested.emit)

        self.filter_edit.textChanged.connect(lambda value: self._apply_filter_change(lambda: self.proxy.set_query(value)))
        self.findings_only.toggled.connect(lambda enabled: self._apply_filter_change(lambda: self.proxy.set_findings_only(enabled)))
        self.animated_only.toggled.connect(lambda enabled: self._apply_filter_change(lambda: self.proxy.set_animated_only(enabled)))
        self.display_mode.currentTextChanged.connect(self._set_display_mode)
        self.model.visibility_requested.connect(
            lambda path, visible: self.visibility_requested.emit([path], visible)
        )
        self.tree.selectionModel().selectionChanged.connect(self._emit_selection)
        self.tree.clicked.connect(self._remember_primary)
        self._add_shortcuts()

    def set_stage(self, stage):
        self.primary_path = ""
        self.model.set_stage(stage)
        self._rebuild_type_menu()
        self._expansion_before_filter = None
        self.tree.expandToDepth(1)

    def set_comparison_changes(self, changes):
        self.model.set_comparison_changes(changes)
        self.proxy.invalidateFilter()
        self.tree.viewport().update()

    def _set_display_mode(self, mode):
        self.model.set_display_mode(mode)
        self.tree.viewport().update()

    def _comparison_filter_changed(self, *args):
        impacts = {value for (group, value), action in self.comparison_actions.items() if group == "Impact" and action.isChecked()}
        kinds = {value for (group, value), action in self.comparison_actions.items() if group == "Kind" and action.isChecked()}
        count = len(impacts) + len(kinds)
        self.comparison_filter.setText("Comparison: All" if not count else f"Comparison: {count}")
        self._apply_filter_change(lambda: self.proxy.set_comparison_filters(impacts, kinds))

    def set_validation_results(self, results):
        self.model.set_validation_results(results)
        self.proxy.invalidateFilter()
        self.tree.viewport().update()

    def set_hidden_paths(self, paths):
        self.model.set_hidden_paths(paths)

    def set_validation_busy(self, busy):
        self.validation_toggle.setEnabled(not busy)
        self.validation_refresh.setEnabled(
            not busy and self.validation_toggle.isChecked()
        )

        self.validation_toggle.setText("Validating..."
            if busy
            else "Validation"
        )

    def set_validation_enabled(self, enabled):
        self.validation_toggle.blockSignals(True)
        self.validation_toggle.setChecked(bool(enabled))
        self.validation_toggle.blockSignals(False)

        self.model.set_validation_visible(enabled)
        self.validation_refresh.setEnabled(bool(enabled))
        self.tree.viewport().update()

    def _validation_toggled(self, enabled):
        self.model.set_validation_visible(enabled)
        self.validation_refresh.setEnabled(enabled)
        self.tree.viewport().update()
        self.validation_toggled.emit(enabled)

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

    def _apply_filter_change(self, change):
        was_active = self.proxy.filters_active
        if not was_active:
            self._expansion_before_filter = self._expanded_paths()
        change()
        if self.proxy.filters_active:
            self.tree.expandAll()
        elif self._expansion_before_filter is not None:
            self.tree.collapseAll()
            self._restore_expanded_paths(self._expansion_before_filter)
            self._expansion_before_filter = None

    def _rebuild_type_menu(self):
        self.type_menu.clear()
        self.type_actions = {}
        all_action = self.type_menu.addAction("All")
        all_action.setCheckable(True)
        all_action.setChecked(True)
        all_action.toggled.connect(self._all_types_toggled)
        self.all_types_action = all_action
        self.type_menu.addSeparator()
        for type_name in sorted({item.type_name for item in self.model.items.values()}, key=str.lower):
            action = self.type_menu.addAction(type_name)
            action.setCheckable(True)
            action.setChecked(True)
            action.toggled.connect(self._type_filter_changed)
            self.type_actions[type_name] = action
        self.proxy.set_type_filter(self.type_actions, all_types=True)
        self.type_filter.setText("Types: All")

    def _all_types_toggled(self, checked):
        if not checked and all(action.isChecked() for action in self.type_actions.values()):
            return
        for action in self.type_actions.values():
            action.blockSignals(True)
            action.setChecked(checked)
            action.blockSignals(False)
        self._type_filter_changed()

    def _type_filter_changed(self, *args):
        enabled = {name for name, action in self.type_actions.items() if action.isChecked()}
        all_types = len(enabled) == len(self.type_actions)
        self.all_types_action.blockSignals(True)
        self.all_types_action.setChecked(all_types)
        self.all_types_action.blockSignals(False)
        self.type_filter.setText("Types: All" if all_types else f"Types: {len(enabled)}")
        self._apply_filter_change(lambda: self.proxy.set_type_filter(enabled, all_types))

    def _status_filter_changed(self, *args):
        enabled = {name for name, action in self.status_actions.items() if action.isChecked()}
        self.status_filter.setText("Status: All" if not enabled else f"Status: {len(enabled)}")
        self._apply_filter_change(lambda: self.proxy.set_validation_statuses(enabled))

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
