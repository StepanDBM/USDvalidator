from contextlib import asynccontextmanager

from fastapi import FastAPI

from s_usd_service.api.dependencies import get_object_storage
from s_usd_service.api.errors import register_exception_handlers
from s_usd_service.api.router import api_router
from s_usd_service.config import get_settings
from s_usd_service.services.validation_job_worker import ValidationJobWorker


@asynccontextmanager
async def lifespan(app):
    settings = get_settings()
    worker = None
    if settings.validation_worker_enabled:
        worker = ValidationJobWorker(
            get_object_storage(),
            poll_seconds=settings.validation_worker_poll_seconds,
            retry_delay_seconds=settings.validation_job_retry_delay_seconds,
        )
        worker.start()
    app.state.validation_job_worker = worker
    try:
        yield
    finally:
        if worker:
            worker.stop()


def create_application():
    settings = get_settings()
    app = FastAPI(title=settings.service_name, version=settings.service_version, lifespan=lifespan)
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_application()
