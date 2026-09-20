from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from s_usd_service.database.repositories.errors import ConflictError, NotFoundError


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(NotFoundError)
    async def not_found_handler(_: Request, error: NotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(error)})

    @app.exception_handler(ConflictError)
    async def conflict_handler(_: Request, error: ConflictError):
        return JSONResponse(status_code=409, content={"detail": str(error)})
