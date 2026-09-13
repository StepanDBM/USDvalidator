from dataclasses import dataclass

from PySide6.QtCore import QAbstractTableModel, QEvent, QModelIndex, QPoint, Qt
from PySide6.QtGui import QColor, QFontDatabase, QKeySequence, QPainter, QPen, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMessageBox,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from .diff_toolbar import DiffToolbar


CHANGED_COLLAPSE_THRESHOLD = 15
UNCHANGED_COLLAPSE_THRESHOLD = 20
UNCHANGED_CONTEXT_LINES = 3
CHANGE_CONTEXT_LINES = 3
EXPAND_ALL_WARNING_THRESHOLD = 250000
SEPARATOR_HIT_RADIUS = 7


@dataclass(frozen=True)
class DiffSection:
    section_id: int
    start: int
    end: int
    kind: str
    context_lines: int

    @property
    def changed(self):
        return self.kind != "UNCHANGED"


@dataclass(frozen=True)
class ChangeRegion:
    start: int
    end: int


class SideBySideDiffModel(QAbstractTableModel):
    COLUMNS = ("Old", "Previous", "New", "Current")
    OLD_REMOVED = QColor(248, 81, 73, 65)
    NEW_ADDED = QColor(46, 160, 67, 75)
    REMOVED_TEXT = QColor(248, 81, 73)
    ADDED_TEXT = QColor(63, 185, 80)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = ()
        self.sections = {}
        self.change_regions = ()
        self.visible_indices = ()
        self.expanded_sections = set()
        self.changes_only = False

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.visible_indices)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.COLUMNS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.COLUMNS[section]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row = self.rows[self.visible_indices[index.row()]]
        column = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            return self._display_value(row, column)
        if role == Qt.ItemDataRole.BackgroundRole:
            return self._background(row.kind, column)
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._foreground(row.kind, column)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return self._alignment(column)
        if role == Qt.ItemDataRole.ToolTipRole:
            return row.old_text if column == 1 else row.new_text if column == 3 else row.kind
        return None

    def set_rows(self, rows):
        self.beginResetModel()
        self.rows = tuple(rows)
        self.sections = self._find_collapsible_sections()
        self.change_regions = self._find_change_regions()
        self.expanded_sections.clear()
        self.changes_only = False
        self.visible_indices = self._build_visible_indices()
        self.endResetModel()

    def clear(self):
        self.set_rows(())

    def toggle_section(self, section_id):
        section = self.sections.get(section_id)
        if section is None:
            return None

        self.beginResetModel()
        if section_id in self.expanded_sections:
            self.expanded_sections.remove(section_id)
        else:
            self.expanded_sections.add(section_id)
        self.visible_indices = self._build_visible_indices()
        self.endResetModel()
        return section.start

    def collapse_all(self):
        self._set_expanded_sections(set())

    def expand_all(self):
        self._set_expanded_sections(set(self.sections))

    def set_changes_only(self, enabled):
        if self.changes_only == enabled:
            return
        self.beginResetModel()
        self.changes_only = enabled
        self.visible_indices = self._build_visible_indices()
        self.endResetModel()

    def display_row_for_source(self, source_index):
        try:
            return self.visible_indices.index(source_index)
        except ValueError:
            return None

    def section_boundaries(self):
        boundaries = []
        for section in self.sections.values():
            leading = min(section.start + section.context_lines - 1, section.end - 1)
            trailing = max(section.start, section.end - section.context_lines)
            leading_row = self.display_row_for_source(leading)
            trailing_row = self.display_row_for_source(trailing)
            if leading_row is None or trailing_row is None:
                continue
            boundaries.append((section.section_id, leading_row, "after", section.kind))
            if section.section_id in self.expanded_sections:
                boundaries.append((section.section_id, trailing_row, "before", section.kind))
        return tuple(boundaries)

    def section_counts(self):
        changed = sum(section.changed for section in self.sections.values())
        return changed, len(self.sections) - changed

    def _set_expanded_sections(self, section_ids):
        if self.expanded_sections == section_ids:
            return
        self.beginResetModel()
        self.expanded_sections = section_ids
        self.visible_indices = self._build_visible_indices()
        self.endResetModel()

    def _find_collapsible_sections(self):
        sections = {}
        section_id = 0
        index = 0
        while index < len(self.rows):
            start = index
            unchanged = self.rows[index].kind == "UNCHANGED"
            kinds = []
            while index < len(self.rows) and (self.rows[index].kind == "UNCHANGED") == unchanged:
                kinds.append(self.rows[index].kind)
                index += 1

            threshold = UNCHANGED_COLLAPSE_THRESHOLD if unchanged else CHANGED_COLLAPSE_THRESHOLD
            if index - start <= threshold:
                continue

            section_id += 1
            kind = "UNCHANGED" if unchanged else kinds[0] if len(set(kinds)) == 1 else "CHANGED"
            context = UNCHANGED_CONTEXT_LINES if unchanged else 1
            sections[section_id] = DiffSection(section_id, start, index, kind, context)
        return sections

    def _find_change_regions(self):
        regions = []
        index = 0
        while index < len(self.rows):
            if self.rows[index].kind == "UNCHANGED":
                index += 1
                continue
            start = index
            while index < len(self.rows) and self.rows[index].kind != "UNCHANGED":
                index += 1
            regions.append(ChangeRegion(start, index))
        return tuple(regions)

    def _build_visible_indices(self):
        normal = self._normal_visible_indices()
        if not self.changes_only:
            return normal

        allowed = set()
        for region in self.change_regions:
            start = max(0, region.start - CHANGE_CONTEXT_LINES)
            end = min(len(self.rows), region.end + CHANGE_CONTEXT_LINES)
            allowed.update(range(start, end))
        return tuple(index for index in normal if index in allowed)

    def _normal_visible_indices(self):
        sections_by_start = {section.start: section for section in self.sections.values()}
        visible = []
        index = 0
        while index < len(self.rows):
            section = sections_by_start.get(index)
            if section is None:
                visible.append(index)
                index += 1
                continue
            if section.section_id in self.expanded_sections:
                visible.extend(range(section.start, section.end))
            else:
                leading_end = min(section.start + section.context_lines, section.end)
                trailing_start = max(leading_end, section.end - section.context_lines)
                visible.extend(range(section.start, leading_end))
                visible.extend(range(trailing_start, section.end))
            index = section.end
        return tuple(visible)

    @staticmethod
    def _display_value(row, column):
        if column == 0:
            prefix = "-" if row.kind in {"REMOVED", "CHANGED"} else ""
            return "" if row.old_number is None else f"{prefix}{row.old_number}"
        if column == 1:
            return row.old_text
        if column == 2:
            prefix = "+" if row.kind in {"ADDED", "CHANGED"} else ""
            return "" if row.new_number is None else f"{prefix}{row.new_number}"
        return row.new_text

    @classmethod
    def _background(cls, kind, column):
        if kind in {"REMOVED", "CHANGED"} and column in (0, 1):
            return cls.OLD_REMOVED
        if kind in {"ADDED", "CHANGED"} and column in (2, 3):
            return cls.NEW_ADDED
        return None

    @classmethod
    def _foreground(cls, kind, column):
        if kind in {"REMOVED", "CHANGED"} and column == 0:
            return cls.REMOVED_TEXT
        if kind in {"ADDED", "CHANGED"} and column == 2:
            return cls.ADDED_TEXT
        return None

    @staticmethod
    def _alignment(column):
        if column in (0, 2):
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter


class DiffTableView(QTableView):
    SEPARATOR_LINE_WIDTH = 3
    SEPARATOR_DOT_RADIUS = 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hovered_boundary = None
        self.active_source_range = None
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)

    def viewportEvent(self, event):
        handled = super().viewportEvent(event)
        if event.type() == QEvent.Type.Paint:
            self._paint_separators()
        return handled

    def mouseMoveEvent(self, event):
        boundary = self.boundary_at(event.position().toPoint())
        identity = self._boundary_identity(boundary)
        if identity != self.hovered_boundary:
            self.hovered_boundary = identity
            self.setCursor(Qt.CursorShape.PointingHandCursor if boundary else Qt.CursorShape.ArrowCursor)
            self.viewport().update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.hovered_boundary = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.viewport().update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            boundary = self.boundary_at(event.position().toPoint())
            if boundary:
                anchor = self.model().toggle_section(boundary["section_id"])
                self.restore_anchor(anchor)
                self.hovered_boundary = None
                self.viewport().update()
                event.accept()
                return
        super().mousePressEvent(event)

    def visible_boundaries(self):
        model = self.model()
        if model is None or not hasattr(model, "section_boundaries"):
            return ()

        boundaries = []
        for section_id, row, position, kind in model.section_boundaries():
            rect = self.visualRect(model.index(row, 0))
            if not rect.isValid():
                continue
            y = rect.bottom() + 1 if position == "after" else rect.top()
            if not -SEPARATOR_HIT_RADIUS <= y <= self.viewport().height() + SEPARATOR_HIT_RADIUS:
                continue
            identity = section_id, position
            boundaries.append({
                "section_id": section_id,
                "position": position,
                "kind": kind,
                "y": y,
                "hovered": identity == self.hovered_boundary,
            })
        return tuple(boundaries)

    def boundary_at(self, position):
        for boundary in self.visible_boundaries():
            if abs(position.y() - boundary["y"]) <= SEPARATOR_HIT_RADIUS:
                return boundary
        return None

    def restore_anchor(self, source_index):
        if source_index is None:
            return
        row = self.model().display_row_for_source(source_index)
        if row is not None:
            self.scrollTo(self.model().index(row, 0), QAbstractItemView.ScrollHint.PositionAtTop)

    def show_change_region(self, region):
        row = self.model().display_row_for_source(region.start)
        if row is None:
            return
        self.active_source_range = region.start, region.end
        index = self.model().index(row, 0)
        self.setCurrentIndex(index)
        self.selectRow(row)
        self.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtCenter)
        self.viewport().update()

    def _paint_separators(self):
        boundaries = self.visible_boundaries()
        if not boundaries:
            return

        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for boundary in boundaries:
            color = self._separator_color(boundary["kind"], boundary["hovered"])
            width = self.SEPARATOR_LINE_WIDTH + int(boundary["hovered"])
            painter.setPen(QPen(color, width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.setBrush(color)
            y = boundary["y"]
            radius = self.SEPARATOR_DOT_RADIUS
            left = radius + 6
            right = self.viewport().width() - radius - 6
            if right <= left:
                continue
            painter.drawLine(left, y, right, y)
            painter.drawEllipse(QPoint(left, y), radius, radius)
            painter.drawEllipse(QPoint(right, y), radius, radius)
        painter.end()

    @staticmethod
    def _separator_color(kind, hovered):
        if hovered:
            return QColor(88, 166, 255, 255)
        if kind == "ADDED":
            return QColor(63, 185, 80, 230)
        if kind == "REMOVED":
            return QColor(248, 81, 73, 230)
        if kind == "UNCHANGED":
            return QColor(139, 148, 158, 210)
        return QColor(210, 153, 34, 230)

    @staticmethod
    def _boundary_identity(boundary):
        return None if boundary is None else (boundary["section_id"], boundary["position"])


class FileDiffView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = SideBySideDiffModel(self)
        self.current_change_index = -1
        self._build_ui()
        self._create_shortcuts()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.toolbar = DiffToolbar()
        self.table = DiffTableView()
        self.table.setModel(self.model)
        self.table.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self.table.setAlternatingRowColors(False)
        self.table.setWordWrap(False)
        self.table.setShowGrid(False)
        self.table.setSortingEnabled(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(22)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.toolbar.previous_requested.connect(self.previous_change)
        self.toolbar.next_requested.connect(self.next_change)
        self.toolbar.changes_only_toggled.connect(self.set_changes_only)
        self.toolbar.collapse_all_requested.connect(self.collapse_all)
        self.toolbar.expand_all_requested.connect(self.expand_all)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.table, 1)

    def _create_shortcuts(self):
        QShortcut(QKeySequence(Qt.Key.Key_F7), self, activated=self.previous_change)
        QShortcut(QKeySequence(Qt.Key.Key_F8), self, activated=self.next_change)
        QShortcut(QKeySequence("Shift+F7"), self, activated=self.collapse_all)
        QShortcut(QKeySequence("Shift+F8"), self, activated=self.expand_all)

    def set_diff(self, rows):
        self.model.set_rows(rows)
        self.current_change_index = -1
        changed_sections, unchanged_sections = self.model.section_counts()
        self.toolbar.set_summary(
            len(self.model.rows),
            len(self.model.change_regions),
            changed_sections,
            unchanged_sections,
        )
        self.toolbar.changes_only_check.blockSignals(True)
        self.toolbar.changes_only_check.setChecked(False)
        self.toolbar.changes_only_check.blockSignals(False)
        if self.model.rowCount():
            self.table.scrollToTop()
        self.table.viewport().update()

    def clear(self):
        self.model.clear()
        self.current_change_index = -1
        self.toolbar.clear()
        self.table.clearSelection()
        self.table.viewport().update()

    def previous_change(self):
        count = len(self.model.change_regions)
        if not count:
            return
        self.current_change_index = (self.current_change_index - 1) % count
        self._show_current_change()

    def next_change(self):
        count = len(self.model.change_regions)
        if not count:
            return
        self.current_change_index = (self.current_change_index + 1) % count
        self._show_current_change()

    def set_changes_only(self, enabled):
        anchor = self._top_source_index()
        self.model.set_changes_only(enabled)
        self.table.restore_anchor(anchor)
        self._restore_current_change()
        self.table.viewport().update()

    def collapse_all(self):
        anchor = self._top_source_index()
        self.model.collapse_all()
        self.table.restore_anchor(anchor)
        self._restore_current_change()
        self.table.viewport().update()

    def expand_all(self):
        if len(self.model.rows) > EXPAND_ALL_WARNING_THRESHOLD:
            answer = QMessageBox.question(
                self,
                "Expand Large Diff",
                (
                    f"This diff contains {len(self.model.rows):,} rows.\n\n"
                    "Expanding every region may use significant memory. Continue?"
                ),
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        anchor = self._top_source_index()
        self.model.expand_all()
        self.table.restore_anchor(anchor)
        self._restore_current_change()
        self.table.viewport().update()

    def _show_current_change(self):
        region = self.model.change_regions[self.current_change_index]
        self.table.show_change_region(region)
        self.toolbar.set_counter(self.current_change_index, len(self.model.change_regions))

    def _restore_current_change(self):
        if 0 <= self.current_change_index < len(self.model.change_regions):
            self._show_current_change()

    def _top_source_index(self):
        index = self.table.indexAt(QPoint(0, 0))
        if index.isValid():
            return self.model.visible_indices[index.row()]
        return 0 if self.model.rows else None
