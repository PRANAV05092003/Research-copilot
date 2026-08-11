import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ReviewRequest(BaseModel):
    topic: str
    paper_ids: list[uuid.UUID] | None = None
    style: str | None = "academic"
    max_length: int | None = 2000


class CompareRequest(BaseModel):
    paper_ids: list[uuid.UUID]
    aspects: list[str] | None = None


class GapsRequest(BaseModel):
    topic: str | None = None
    paper_ids: list[uuid.UUID] | None = None


class ReportOut(BaseModel):
    id: uuid.UUID
    kind: str
    confidence: float | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ReportDetailOut(ReportOut):
    content_markdown: str
    citations: dict[str, Any] | None
    params: dict[str, Any] | None
    model_config = ConfigDict(from_attributes=True)


class ComparisonOut(BaseModel):
    comparison_table: dict[str, Any]
    markdown: str
