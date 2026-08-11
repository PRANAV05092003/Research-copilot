import uuid

from pydantic import BaseModel


class SearchFilters(BaseModel):
    paper_ids: list[uuid.UUID] | None = None
    year_from: int | None = None
    year_to: int | None = None

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    filters: SearchFilters | None = None
    mode: str = "hybrid" # "hybrid", "semantic", "keyword"

class SearchResultItem(BaseModel):
    chunk_id: uuid.UUID
    paper_id: uuid.UUID
    paper_title: str | None
    text: str
    page_number: int | None
    score: float

class SearchResponse(BaseModel):
    results: list[SearchResultItem]
    query: str
    took_ms: int
    mode: str
