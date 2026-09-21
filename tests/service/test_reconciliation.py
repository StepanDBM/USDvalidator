from io import BytesIO
from uuid import uuid4

from s_usd_service.database.models import Asset, Project, StoredFile, Stream, Version
from s_usd_service.database.session import SessionLocal
from s_usd_service.services.file_lifecycle import FileLifecycleService
from s_usd_service.services.reconciliation import StorageReconciliationService
from s_usd_service.storage.local import LocalObjectStorage


def seed_file(database, storage, key="projects/ORBIT/assets/rover/v0001/root.usda"):
    project = Project(code=f"P{uuid4().hex[:8]}", name="Orbit")
    asset = Asset(project=project, code="rover", name="Rover", asset_type="prop")
    stream = Stream(asset=asset, name="model")
    version = Version(stream=stream, number=1, status="uploaded")
    result = storage.write_stream(BytesIO(b"#usda 1.0\n"), key)
    stored_file = StoredFile(
        version=version,
        role="root_layer",
        original_name="root.usda",
        relative_path="root.usda",
        storage_key=result.storage_key,
        content_type="application/octet-stream",
        size_bytes=result.size_bytes,
        sha256=result.sha256,
        status="available"
    )
    database.add(stored_file)
    database.commit()
    database.refresh(stored_file)
    return stored_file


def test_safe_delete_removes_object_and_metadata(tmp_path):
    storage = LocalObjectStorage(tmp_path / "storage", tmp_path / "temp")

    with SessionLocal() as database:
        stored_file = seed_file(database, storage)
        file_id = stored_file.id
        key = stored_file.storage_key
        result = FileLifecycleService(database, storage).delete(file_id)

        assert result["object_existed"] is True
        assert result["metadata_deleted"] is True
        assert storage.exists(key) is False
        assert database.get(StoredFile, file_id) is None


def test_safe_delete_removes_metadata_when_object_is_already_missing(tmp_path):
    storage = LocalObjectStorage(tmp_path / "storage", tmp_path / "temp")

    with SessionLocal() as database:
        stored_file = seed_file(database, storage)
        file_id = stored_file.id
        storage.delete(stored_file.storage_key)
        result = FileLifecycleService(database, storage).delete(file_id)

        assert result["object_existed"] is False
        assert database.get(StoredFile, file_id) is None


def test_reconciliation_detects_and_repairs_inconsistency(tmp_path):
    storage = LocalObjectStorage(tmp_path / "storage", tmp_path / "temp")

    with SessionLocal() as database:
        stored_file = seed_file(database, storage)
        missing_key = stored_file.storage_key
        storage.delete(missing_key)
        orphaned_key = "projects/NEBULA/assets/orphan/root.usda"
        storage.write_stream(BytesIO(b"orphan"), orphaned_key)
        service = StorageReconciliationService(database, storage)

        dry_run = service.reconcile()
        assert dry_run.consistent is False
        assert dry_run.missing_database_objects == [missing_key]
        assert dry_run.orphaned_storage_objects == [orphaned_key]
        assert stored_file.status == "available"
        assert storage.exists(orphaned_key) is True

        repaired = service.reconcile(repair=True, delete_orphans=True)
        database.refresh(stored_file)
        assert stored_file.status == "missing"
        assert repaired.marked_missing_records == [missing_key]
        assert repaired.deleted_orphaned_objects == [orphaned_key]
        assert storage.exists(orphaned_key) is False


def test_reconciliation_restores_record_status_when_file_returns(tmp_path):
    storage = LocalObjectStorage(tmp_path / "storage", tmp_path / "temp")

    with SessionLocal() as database:
        stored_file = seed_file(database, storage)
        key = stored_file.storage_key
        storage.delete(key)
        service = StorageReconciliationService(database, storage)
        service.reconcile(repair=True)
        database.refresh(stored_file)
        assert stored_file.status == "missing"

        storage.write_stream(BytesIO(b"#usda 1.0\n"), key)
        report = service.reconcile(repair=True)
        database.refresh(stored_file)
        assert stored_file.status == "available"
        assert report.restored_records == [key]


def test_delete_keeps_metadata_when_storage_delete_fails(tmp_path):
    class FailingDeleteStorage(LocalObjectStorage):
        def delete(self, storage_key):
            raise OSError("Simulated storage failure")

    storage = FailingDeleteStorage(tmp_path / "storage", tmp_path / "temp")

    with SessionLocal() as database:
        stored_file = seed_file(database, storage)
        file_id = stored_file.id

        import pytest

        with pytest.raises(OSError, match="Simulated storage failure"):
            FileLifecycleService(database, storage).delete(file_id)

        assert database.get(StoredFile, file_id) is not None


def test_repair_reports_consistency_before_and_after(tmp_path):
    storage = LocalObjectStorage(tmp_path / "storage", tmp_path / "temp")

    with SessionLocal() as database:
        orphaned_key = "projects/COSMOS/orphan/root.usda"
        storage.write_stream(BytesIO(b"orphan"), orphaned_key)
        report = StorageReconciliationService(database, storage).reconcile(
            repair=True,
            delete_orphans=True
        )

        assert report.consistent_before is False
        assert report.consistent_after is True
