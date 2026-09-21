from dataclasses import asdict, dataclass, field

from s_usd_service.database.repositories.files import StoredFileRepository


@dataclass
class ReconciliationReport:
    database_records: int = 0
    storage_objects: int = 0
    missing_database_objects: list[str] = field(default_factory=list)
    orphaned_storage_objects: list[str] = field(default_factory=list)
    restored_records: list[str] = field(default_factory=list)
    marked_missing_records: list[str] = field(default_factory=list)
    deleted_orphaned_objects: list[str] = field(default_factory=list)
    consistent_after: bool | None = None

    @property
    def consistent_before(self):
        return not self.missing_database_objects and not self.orphaned_storage_objects

    @property
    def consistent(self):
        return self.consistent_before

    def to_dict(self):
        return {
            "consistent": self.consistent_before,
            "consistent_before": self.consistent_before,
            **asdict(self)
        }


class StorageReconciliationService:
    def __init__(self, database, storage):
        self.database = database
        self.storage = storage
        self.files = StoredFileRepository(database)

    def reconcile(self, repair=False, delete_orphans=False):
        records = self.files.list_all()
        records_by_key = {item.storage_key: item for item in records}
        storage_keys = set(self.storage.iter_keys())
        database_keys = set(records_by_key)
        missing_keys = sorted(database_keys - storage_keys)
        orphaned_keys = sorted(storage_keys - database_keys)
        report = ReconciliationReport(
            database_records=len(records),
            storage_objects=len(storage_keys),
            missing_database_objects=missing_keys,
            orphaned_storage_objects=orphaned_keys
        )

        if repair:
            self._repair_records(records_by_key, missing_keys, report)

            if delete_orphans:
                for storage_key in orphaned_keys:
                    if self.storage.delete(storage_key):
                        report.deleted_orphaned_objects.append(storage_key)

            self.files.commit()
            report.consistent_after = self._is_consistent()
        else:
            report.consistent_after = report.consistent_before

        return report

    def _is_consistent(self):
        database_keys = {item.storage_key for item in self.files.list_all()}
        storage_keys = set(self.storage.iter_keys())
        return database_keys == storage_keys

    @staticmethod
    def _repair_records(records_by_key, missing_keys, report):
        missing_set = set(missing_keys)

        for storage_key, record in records_by_key.items():
            if storage_key in missing_set:
                if record.status != "missing":
                    record.status = "missing"
                    report.marked_missing_records.append(storage_key)
            elif record.status == "missing":
                record.status = "available"
                report.restored_records.append(storage_key)
