import typing
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.error_handler import setup_exception_handlers
from app.api.v1.router import api_router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> typing.Any:
    # Startup logic: init DB connections, etc. if needed
    yield
    # Shutdown logic

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="API for Research Copilot",
        openapi_url="/openapi.json",
        docs_url="/docs",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_exception_handlers(app)

    # We will add other middleware (e.g. rate limit, request_id) here later.

    app.include_router(api_router, prefix="/api/v1")

    @app.get("/")
    async def root() -> typing.Any:
        return {
            "name": settings.APP_NAME,
            "version": "0.1.0",
            "docs_url": "/docs"
        }

    return app

app = create_app()
