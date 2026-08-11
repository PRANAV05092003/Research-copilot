import typing

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter()

@router.get("/health/live")
async def health_live() -> typing.Any:
    return {"status": "ok"}

@router.get("/health/ready")
async def health_ready(db: AsyncSession = Depends(get_db)) -> typing.Any:
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception:
        # We would normally return 503 here
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database not ready")
