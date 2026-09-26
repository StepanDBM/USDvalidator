from s_usd_desktop.ui.tooltips import TooltipText

from PySide6.QtCore import QAbstractListModel, QAbstractTableModel, QModelIndex, Qt


class RecordListModel(QAbstractListModel):
    IdRole = Qt.UserRole + 1
    RecordRole = Qt.UserRole + 2

    def __init__(self, display_getter, parent=None):
        super().__init__(parent)
        self.display_getter = display_getter
        self.records = ()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.records)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self.records):
            return None

        record = self.records[index.row()]

        if role == Qt.DisplayRole:
            return self.display_getter(record)
        if role == Qt.ToolTipRole:
            kind = type(self).__name__
            explanation = {
                "ProjectListModel": TooltipText.PROJECT_ROW,
                "AssetListModel": TooltipText.ASSET_ROW,
                "StreamListModel": TooltipText.STREAM_ROW
            }.get(kind, TooltipText.STORAGE_WORKSPACE)
            values = [f"{explanation}", "", f"Name: {getattr(record, 'name', '')}"]
            code = getattr(record, "code", "")
            description = getattr(record, "description", "")
            if code:
                values.append(f"Code: {code}")
            if description:
                values.append(f"Description: {description}")
            return "\n".join(values)
        if role == self.IdRole:
            return record.id
        if role == self.RecordRole:
            return record
        return None

    def set_records(self, records):
        self.beginResetModel()
        self.records = tuple(records)
        self.endResetModel()

    def clear(self):
        self.set_records(())

    def record_at(self, row):
        return self.records[row] if 0 <= row < len(self.records) else None


class ProjectListModel(RecordListModel):
    def __init__(self, parent=None):
        super().__init__(lambda record: f"{record.code}  {record.name}", parent)


class AssetListModel(RecordListModel):
    def __init__(self, parent=None):
        super().__init__(lambda record: f"{record.code}  {record.name}", parent)


class StreamListModel(RecordListModel):
    def __init__(self, parent=None):
        super().__init__(lambda record: record.name, parent)


class VersionTableModel(QAbstractTableModel):
    HEADERS = ("Version", "Status", "Comment", "Updated")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.records = ()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.records)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.HEADERS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self.records):
            return None

        record = self.records[index.row()]

        if role == Qt.UserRole:
            return record
        if role == Qt.ToolTipRole:
            return (f"{TooltipText.VERSION_ROW}\n\n"
                    f"Number: {getattr(record, 'number', '')}\n"
                    f"Status: {getattr(record, 'status', '')}")
        if role != Qt.DisplayRole:
            return None

        values = (
            record.display_name,
            record.status,
            record.comment,
            record.updated_at.strftime("%Y-%m-%d %H:%M")
        )
        return values[index.column()]

    def set_records(self, records):
        self.beginResetModel()
        self.records = tuple(records)
        self.endResetModel()

    def clear(self):
        self.set_records(())

    def record_at(self, row):
        return self.records[row] if 0 <= row < len(self.records) else None


class StoredFileTableModel(QAbstractTableModel):
    HEADERS = ("Role", "Path", "Size", "Remote", "Cache")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.records = ()
        self.cache_statuses = {}

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.records)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.HEADERS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self.records):
            return None

        record = self.records[index.row()]

        if role == Qt.UserRole:
            return record
        if role == Qt.ToolTipRole:
            return (f"{TooltipText.STORED_FILE_ROW}\n\n"
                    f"Relative Path: {getattr(record, 'relative_path', '')}\n"
                    f"Role: {getattr(record, 'role', '')}")
        if role != Qt.DisplayRole:
            return None

        status = self.cache_statuses.get(record.id, "Not cached")
        values = (
            record.role,
            record.relative_path,
            self.format_size(record.size_bytes),
            record.status,
            status
        )
        return values[index.column()]

    def set_records(self, records):
        self.beginResetModel()
        self.records = tuple(records)
        self.cache_statuses = {}
        self.endResetModel()

    def set_cache_status(self, file_id, status):
        self.cache_statuses[file_id] = status
        row = next((i for i, record in enumerate(self.records) if record.id == file_id), -1)
        if row >= 0:
            index = self.index(row, 4)
            self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def clear(self):
        self.set_records(())

    def record_at(self, row):
        return self.records[row] if 0 <= row < len(self.records) else None

    @staticmethod
    def format_size(size):
        value = float(size)

        for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
            if value < 1024 or unit == "TiB":
                return f"{int(value)} {unit}" if unit == "B" else f"{value:.1f} {unit}"
            value /= 1024

class ValidationHistoryTableModel(QAbstractTableModel):
    HEADERS = ("Result", "Profile", "Checks", "Failed", "Warnings", "Tool", "Completed")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.records = ()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.records)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.HEADERS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self.records):
            return None

        record = self.records[index.row()]

        if role == Qt.UserRole:
            return record
        if role == Qt.ToolTipRole:
            return (f"{TooltipText.VALIDATION_HISTORY_ROW}\n\n"
                    f"Profile Name: {getattr(record, 'profile_name', '')}\n"
                    f"Publish Passed: {getattr(record, 'publish_passed', '')}")
        if role != Qt.DisplayRole:
            return None

        values = (
            "Passed" if record.publish_passed else "Failed",
            record.profile_name,
            record.total_count,
            record.failed_count + record.error_count,
            record.warning_count,
            f"{record.tool_name} {record.tool_version}",
            record.completed_at.strftime("%Y-%m-%d %H:%M:%S")
        )
        return values[index.column()]

    def set_records(self, records):
        self.beginResetModel()
        self.records = tuple(records)
        self.endResetModel()

    def clear(self):
        self.set_records(())

    def record_at(self, row):
        return self.records[row] if 0 <= row < len(self.records) else None
