import typing
import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_current_user, get_research_agent_service, get_current_workspace_id
from app.models import User
from app.services.interfaces import ConcreteResearchAgentService

router = APIRouter()

class ReviewRequest(BaseModel):
    topic: str

@router.post("/review", status_code=202)
async def generate_review(
    req: ReviewRequest,
    service: ConcreteResearchAgentService = Depends(get_research_agent_service),
    current_user: User = Depends(get_current_user),
    workspace_id: uuid.UUID = Depends(get_current_workspace_id)
) -> typing.Any:
    
    job_id = await service.generate_deep_review(req.topic, current_user.id, workspace_id)
    return {"job_id": job_id}
