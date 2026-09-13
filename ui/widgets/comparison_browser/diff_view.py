from dataclasses import dataclass

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor, QFontDatabase
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableView,
    QVBoxLayout,
    QWidget,
)


COLLAPSE_THRESHOLD = 15


@dataclass(frozen=True)
class DiffSection:
    section_id: int
    start: int
    end: int

    @property
    def row_count(self):
        return self.end - self.start

    @property
    def hidden_count(self):
        return max(0, self.row_count - 2)


@dataclass(frozen=True)
class DisplayRow:
    source_index: int | None = None
    section_id: int | None = None

    @property
    def is_control(self):
        return self.section_id is not None


class SideBySideDiffModel(QAbstractTableModel):
    COLUMNS = ("Old", "Previous", "New", "Current")
    CONTROL_ROLE = Qt.ItemDataRole.UserRole + 1

    OLD_REMOVED = QColor(248, 81, 73, 65)
    NEW_ADDED = QColor(46, 160, 67, 75)
    CONTROL_BACKGROUND = QColor(56, 139, 253, 45)
    CONTROL_FOREGROUND = QColor(88, 166, 255)
    REMOVED_FOREGROUND = QColor(248, 81, 73)
    ADDED_FOREGROUND = QColor(63, 185, 80)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = ()
        self.sections = {}
        self.display_rows = ()
        self.expanded_sections = set()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.display_rows)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.COLUMNS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.COLUMNS[section]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        display_row = self.display_rows[index.row()]
        if display_row.is_control:
            return self._control_data(display_row.section_id, index.column(), role)

        row = self.rows[display_row.source_index]
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
        if role == self.CONTROL_ROLE:
            return False
        return None

    def set_rows(self, rows):
        self.beginResetModel()
        self.rows = tuple(rows)
        self.sections = self._find_sections()
        self.expanded_sections.clear()
        self.display_rows = self._create_display_rows()
        self.endResetModel()

    def clear(self):
        self.set_rows(())

    def is_control_row(self, row):
        return 0 <= row < len(self.display_rows) and self.display_rows[row].is_control

    def toggle_section(self, display_row):
        if not self.is_control_row(display_row):
            return False

        section_id = self.display_rows[display_row].section_id
        self.beginResetModel()
        if section_id in self.expanded_sections:
            self.expanded_sections.remove(section_id)
        else:
            self.expanded_sections.add(section_id)
        self.display_rows = self._create_display_rows()
        self.endResetModel()
        return True

    def _find_sections(self):
        sections = {}
        section_id = 0
        index = 0

        while index < len(self.rows):
            if self.rows[index].kind == "UNCHANGED":
                index += 1
                continue

            start = index
            while index < len(self.rows) and self.rows[index].kind != "UNCHANGED":
                index += 1

            end = index
            if end - start > COLLAPSE_THRESHOLD:
                section_id += 1
                sections[section_id] = DiffSection(section_id, start, end)

        return sections

    def _create_display_rows(self):
        sections_by_start = {section.start: section for section in self.sections.values()}
        display_rows = []
        index = 0

        while index < len(self.rows):
            section = sections_by_start.get(index)
            if section is None:
                display_rows.append(DisplayRow(source_index=index))
                index += 1
                continue

            display_rows.append(DisplayRow(source_index=section.start))
            display_rows.append(DisplayRow(section_id=section.section_id))

            if section.section_id in self.expanded_sections:
                for source_index in range(section.start + 1, section.end):
                    display_rows.append(DisplayRow(source_index=source_index))
            else:
                display_rows.append(DisplayRow(source_index=section.end - 1))

            index = section.end

        return tuple(display_rows)

    def _control_data(self, section_id, column, role):
        section = self.sections[section_id]
        expanded = section_id in self.expanded_sections

        if role == Qt.ItemDataRole.DisplayRole:
            if column not in (1, 3):
                return ""
            marker = "Collapse" if expanded else "Expand"
            state = "shown" if expanded else "hidden"
            return f"{marker} {section.hidden_count:,} changed lines ({state})"
        if role == Qt.ItemDataRole.BackgroundRole:
            return self.CONTROL_BACKGROUND
        if role == Qt.ItemDataRole.ForegroundRole:
            return self.CONTROL_FOREGROUND
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        if role == Qt.ItemDataRole.ToolTipRole:
            return "Click to collapse this changed region." if expanded else "Click to expand this changed region."
        if role == self.CONTROL_ROLE:
            return True
        return None

    @staticmethod
    def _display_value(row, column):
        if column == 0:
            if row.old_number is None:
                return ""
            prefix = "-" if row.kind in {"REMOVED", "CHANGED"} else ""
            return f"{prefix}{row.old_number}"
        if column == 1:
            return row.old_text
        if column == 2:
            if row.new_number is None:
                return ""
            prefix = "+" if row.kind in {"ADDED", "CHANGED"} else ""
            return f"{prefix}{row.new_number}"
        return row.new_text

    @classmethod
    def _background(cls, kind, column):
        if kind == "REMOVED" and column in (0, 1):
            return cls.OLD_REMOVED
        if kind == "ADDED" and column in (2, 3):
            return cls.NEW_ADDED
        if kind == "CHANGED":
            if column in (0, 1):
                return cls.OLD_REMOVED
            if column in (2, 3):
                return cls.NEW_ADDED
        return None

    @classmethod
    def _foreground(cls, kind, column):
        if column == 0 and kind in {"REMOVED", "CHANGED"}:
            return cls.REMOVED_FOREGROUND
        if column == 2 and kind in {"ADDED", "CHANGED"}:
            return cls.ADDED_FOREGROUND
        return None

    @staticmethod
    def _alignment(column):
        if column in (0, 2):
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter


class FileDiffView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = SideBySideDiffModel(self)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableView()
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

        self.table.clicked.connect(self._toggle_clicked_section)
        layout.addWidget(self.table)

    def set_diff(self, rows):
        self.model.set_rows(rows)
        if self.model.rowCount():
            self.table.scrollToTop()

    def clear(self):
        self.model.clear()

    def _toggle_clicked_section(self, index):
        if not self.model.is_control_row(index.row()):
            return

        section_id = self.model.display_rows[index.row()].section_id
        section = self.model.sections[section_id]
        expanded = section_id in self.model.expanded_sections
        target_source_index = section.start
        self.model.toggle_section(index.row())
        target_row = self._display_row_for_source(target_source_index)

        if target_row is not None:
            target = self.model.index(target_row, 0)
            self.table.scrollTo(target, QAbstractItemView.ScrollHint.PositionAtTop)

        if expanded:
            self.table.clearSelection()

    def _display_row_for_source(self, source_index):
        for display_index, row in enumerate(self.model.display_rows):
            if row.source_index == source_index:
                return display_index
        return None
