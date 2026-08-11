import typing
import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_rag_service, get_current_workspace_id
from app.models import User
from app.schemas.search import SearchRequest, SearchResponse
from app.services.interfaces import ConcreteRAGService

router = APIRouter()

@router.post("", response_model=SearchResponse)
async def search_papers(
    request: SearchRequest,
    service: ConcreteRAGService = Depends(get_rag_service),
    current_user: User = Depends(get_current_user),
    workspace_id: uuid.UUID = Depends(get_current_workspace_id)
) -> typing.Any:
    import time
    start = time.perf_counter()
    raw_results = await service.hybrid_search(request.query, workspace_id, request.top_k)
    took = int((time.perf_counter() - start) * 1000)
    
    from app.schemas.search import SearchResultItem
    results = [
        SearchResultItem(
            chunk_id=r["chunk_id"],
            paper_id=r["paper_id"],
            paper_title=r.get("paper_title"),
            text=r["text"],
            page_number=r.get("page_number"),
            score=r.get("score", 0.0)
        ) for r in raw_results
    ]
    
    return SearchResponse(results=results, query=request.query, took_ms=took, mode=request.mode)
