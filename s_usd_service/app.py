from fastapi import FastAPI

from s_usd_service.api.errors import register_exception_handlers
from s_usd_service.api.router import api_router
from s_usd_service.config import get_settings


def create_application():
    settings = get_settings()
    app = FastAPI(title=settings.service_name, version=settings.service_version)
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_application()
