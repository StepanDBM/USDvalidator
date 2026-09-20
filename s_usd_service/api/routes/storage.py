from fastapi import APIRouter, Query

from s_usd_service.api.dependencies import DatabaseSession, ObjectStorageDependency
from s_usd_service.api.schemas.storage import ReconciliationResponse
from s_usd_service.services.reconciliation import StorageReconciliationService

router = APIRouter(prefix="/storage", tags=["Storage"])


@router.post("/reconcile", response_model=ReconciliationResponse)
def reconcile_storage(
    database: DatabaseSession,
    storage: ObjectStorageDependency,
    repair: bool = Query(default=False),
    delete_orphans: bool = Query(default=False)
):
    if delete_orphans:
        repair = True

    report = StorageReconciliationService(database, storage).reconcile(
        repair=repair,
        delete_orphans=delete_orphans
    )
    return report.to_dict()
