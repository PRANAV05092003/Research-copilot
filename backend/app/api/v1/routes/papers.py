import typing
import uuid

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import get_current_user, get_paper_ingestion_service, get_paper_repo, get_current_workspace_id
from app.db.repositories import SQLAlchemyPaperRepository
from app.models import User
from app.schemas.common import Page
from app.schemas.paper import PaperOut
from app.services.interfaces import ConcretePaperIngestionService

router = APIRouter()

@router.post("/upload", status_code=202)
async def upload_paper(
    file: UploadFile = File(...),
    service: ConcretePaperIngestionService = Depends(get_paper_ingestion_service),
    current_user: User = Depends(get_current_user),
    workspace_id: uuid.UUID = Depends(get_current_workspace_id)
) -> typing.Any:
    file_bytes = await file.read()
    
    filename = file.filename or "unnamed_paper.pdf"
    job_id = await service.enqueue_paper(file_bytes, filename, current_user.id, workspace_id)
    return {"job_id": job_id}

@router.get("", response_model=Page[PaperOut])
async def list_papers(
    cursor: str | None = None, limit: int = 20,
    paper_repo: SQLAlchemyPaperRepository = Depends(get_paper_repo),
    workspace_id: uuid.UUID = Depends(get_current_workspace_id)
) -> typing.Any:
    papers = await paper_repo.list_by_workspace(workspace_id, limit)
    
    return Page(items=papers, next_cursor=None, count=len(papers))
