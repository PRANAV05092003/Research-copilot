import uuid

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.errors import AppError

logger = structlog.get_logger()


def setup_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        request_id = (
            request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4())
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": exc.type,
                "title": exc.title,
                "status": exc.status_code,
                "detail": exc.detail,
                "instance": exc.instance or str(request.url),
                "request_id": request_id,
                **exc.extra,
            },
            headers={"Content-Type": "application/problem+json"},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = (
            request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4())
        )
        errors = [
            {"loc": err["loc"], "msg": err["msg"], "type": err["type"]} for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "type": "https://example.com/probs/validation",
                "title": "Unprocessable Entity",
                "status": 422,
                "detail": "Request validation failed.",
                "instance": str(request.url),
                "request_id": request_id,
                "errors": errors,
            },
            headers={"Content-Type": "application/problem+json"},
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.exception("Database error occurred", error=str(exc))
        request_id = (
            request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4())
        )
        return JSONResponse(
            status_code=503,
            content={
                "type": "https://example.com/probs/database",
                "title": "Service Unavailable",
                "status": 503,
                "detail": "Database error occurred.",
                "instance": str(request.url),
                "request_id": request_id,
            },
            headers={"Content-Type": "application/problem+json"},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception", error=str(exc))
        request_id = (
            request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4())
        )
        return JSONResponse(
            status_code=500,
            content={
                "type": "about:blank",
                "title": "Internal Server Error",
                "status": 500,
                "detail": "An unexpected error occurred.",
                "instance": str(request.url),
                "request_id": request_id,
            },
            headers={"Content-Type": "application/problem+json"},
        )
