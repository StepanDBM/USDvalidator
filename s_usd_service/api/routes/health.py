from fastapi import APIRouter

from s_usd_service.api.schemas.common import HealthResponse
from s_usd_service.config import get_settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def get_health():
    settings = get_settings()
    return HealthResponse(status="healthy", service=settings.service_name, version=settings.service_version)
