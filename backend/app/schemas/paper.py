import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class PaperOut(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    title: str | None = None
    authors: dict[str, Any] | None = None
    year: int | None = None
    doi: str | None = None
    venue: str | None = None
    abstract: str | None = None
    status: str
    page_count: int | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PaperUpdate(BaseModel):
    title: str | None = None
    year: int | None = None
    venue: str | None = None

class JobOut(BaseModel):
    id: uuid.UUID
    type: str
    status: str
    progress: int
    error: str | None = None
    model_config = ConfigDict(from_attributes=True)
