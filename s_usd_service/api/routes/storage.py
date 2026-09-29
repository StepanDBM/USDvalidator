from fastapi import APIRouter, HTTPException, Query, status

from s_usd_service.api.dependencies import CurrentUser, DatabaseSession, ObjectStorageDependency
from s_usd_service.api.schemas.storage import ReconciliationResponse
from s_usd_service.services.reconciliation import StorageReconciliationService

router = APIRouter(prefix="/storage", tags=["Storage"])


@router.post("/reconcile", response_model=ReconciliationResponse)
def reconcile_storage(
    database: DatabaseSession,
    storage: ObjectStorageDependency,
    current_user: CurrentUser,
    repair: bool = Query(default=False),
    delete_orphans: bool = Query(default=False),
):
    if not current_user.is_platform_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Global storage reconciliation requires platform-administrator access.",
        )
    if delete_orphans:
        repair = True
    return (
        StorageReconciliationService(database, storage)
        .reconcile(repair=repair, delete_orphans=delete_orphans)
        .to_dict()
    )
