from fastapi import APIRouter

from .routes import auth, conversations, health, jobs, papers, research, search

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(papers.router, prefix="/papers", tags=["papers"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(research.router, prefix="/research", tags=["research"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
