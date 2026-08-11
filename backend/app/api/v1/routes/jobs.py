import typing
import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_job_service
from app.core.errors import AppError
from app.models import User
from app.schemas.paper import JobOut
from app.services.interfaces import ConcreteJobService

router = APIRouter()


@router.get("/{id}", response_model=JobOut)
async def get_job(
    id: uuid.UUID,
    service: ConcreteJobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user),
) -> typing.Any:

    job = await service.get_job_status(id)
    if not job:
        raise AppError(status_code=404, title="Not Found", detail="Job not found")
    return job
