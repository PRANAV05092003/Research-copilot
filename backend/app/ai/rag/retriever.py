import abc
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers.base import EmbeddingProvider
from app.models import Paper, PaperChunk


class BaseRetriever(abc.ABC):
    @abc.abstractmethod
    async def retrieve(
        self, 
        query: str, 
        top_k: int = 10, 
        workspace_id: uuid.UUID | None = None,
        paper_ids: list[uuid.UUID] | None = None
    ) -> list[dict[str, Any]]:
        pass

class PgVectorRetriever(BaseRetriever):
    def __init__(self, session: AsyncSession, embedding_provider: EmbeddingProvider):
        self.session = session
        self.embedding_provider = embedding_provider

    async def retrieve(
        self, 
        query: str, 
        top_k: int = 10, 
        workspace_id: uuid.UUID | None = None,
        paper_ids: list[uuid.UUID] | None = None
    ) -> list[dict[str, Any]]:
        
        # 1. Embed query
        query_embedding = await self.embedding_provider.embed_documents([query])
        query_vector = query_embedding[0]
        
        # 2. Semantic Search Query
        stmt = select(PaperChunk, Paper).join(Paper, PaperChunk.paper_id == Paper.id)
        
        # 3. Metadata Filters
        if workspace_id:
            stmt = stmt.where(Paper.workspace_id == workspace_id)
        if paper_ids:
            stmt = stmt.where(Paper.id.in_(paper_ids))
            
        # 4. Hybrid Search logic (Semantic + Keyword)
        # In a real postgres environment with pgvector, we order by cosine distance.
        # And we can use ILIKE for exact keyword match boosting.
        PaperChunk.text.ilike(f"%{query}%")
        
        # We order by cosine distance
        stmt = stmt.order_by(PaperChunk.embedding.cosine_distance(query_vector))
        stmt = stmt.limit(top_k * 2) # Fetch more for reciprocal rank fusion or filtering
        
        result = await self.session.execute(stmt)
        rows = result.all()
        
        # Format results
        out = []
        for chunk, paper in rows:
            out.append({
                "paper_id": str(paper.id),
                "chunk_id": str(chunk.id),
                "text": chunk.text,
                "page_number": chunk.page_number,
                "paper_title": paper.title,
                "score": 0.9 # We would normally extract the raw distance here, mock 0.9 for now
            })
            
        # 5. Simple Reciprocal Rank Fusion (RRF) placeholder
        # Since we just combined, we take the top_k
        return out[:top_k]
