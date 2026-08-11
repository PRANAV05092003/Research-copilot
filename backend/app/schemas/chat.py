import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class CitationOut(BaseModel):
    id: uuid.UUID
    paper_id: uuid.UUID | None
    chunk_id: uuid.UUID | None
    claim_text: str
    quoted_text: str | None
    page_number: int | None
    position: int | None
    verification_status: str
    verification_score: float | None
    model_config = ConfigDict(from_attributes=True)


class MessageOut(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    citations: list[CitationOut] = []
    confidence: float | None = None
    tokens: dict[str, Any] | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ConversationOut(BaseModel):
    id: uuid.UUID
    title: str | None
    mode: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ConversationDetailOut(ConversationOut):
    messages: list[MessageOut] = []
    model_config = ConfigDict(from_attributes=True)


class MessageCreate(BaseModel):
    content: str
    mode: str = "standard"  # "standard" | "deep_research"
