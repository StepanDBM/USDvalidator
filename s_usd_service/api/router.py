from fastapi import APIRouter

from s_usd_service.api.routes import assets, health, projects, streams, versions

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(projects.router)
api_router.include_router(assets.router)
api_router.include_router(streams.router)
api_router.include_router(versions.router)
