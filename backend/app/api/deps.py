from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers.base import EmbeddingProvider, LLMProvider
from app.ai.rag.compressor import ContextCompressor
from app.ai.rag.retriever import PgVectorRetriever
from app.ai.verification.citation_verifier import CitationVerifier
from app.core.errors import AppError
from app.core.security import decode_access_token
from app.db.repositories import (
    SQLAlchemyConversationRepository,
    SQLAlchemyJobRepository,
    SQLAlchemyPaperRepository,
)
from app.db.session import get_db
from app.models import User
from app.services.interfaces import (
    ConcreteConversationService,
    ConcreteJobService,
    ConcretePaperIngestionService,
    ConcreteRAGService,
    ConcreteResearchAgentService,
)

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("No subject in token")
    except Exception:
        raise AppError(status_code=401, title="Unauthorized", detail="Could not validate credentials")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise AppError(status_code=401, title="Unauthorized", detail="User not found or inactive")
        
    return user

async def get_paper_repo(db: AsyncSession = Depends(get_db)) -> SQLAlchemyPaperRepository:
    return SQLAlchemyPaperRepository(db)

async def get_job_repo(db: AsyncSession = Depends(get_db)) -> SQLAlchemyJobRepository:
    return SQLAlchemyJobRepository(db)

async def get_conv_repo(db: AsyncSession = Depends(get_db)) -> SQLAlchemyConversationRepository:
    return SQLAlchemyConversationRepository(db)

async def get_llm_provider() -> LLMProvider:
    from app.config import settings
    if settings.LLM_PROVIDER == "openai":
        from app.ai.providers.openai import OpenAILLMProvider
        return OpenAILLMProvider()
    else:
        from app.ai.providers.mock import MockLLMProvider
        return MockLLMProvider()

async def get_embedding_provider() -> EmbeddingProvider:
    from app.config import settings
    if settings.EMBEDDING_PROVIDER == "sentence-transformers":
        from app.ai.providers.sentence_transformers import SentenceTransformersEmbeddingProvider
        return SentenceTransformersEmbeddingProvider()
    else:
        from app.ai.providers.mock import HashEmbeddingProvider
        return HashEmbeddingProvider()

async def get_rag_service(
    db: AsyncSession = Depends(get_db),
    paper_repo: SQLAlchemyPaperRepository = Depends(get_paper_repo),
    embedding_provider: EmbeddingProvider = Depends(get_embedding_provider),
    llm: LLMProvider = Depends(get_llm_provider)
) -> ConcreteRAGService:
    retriever = PgVectorRetriever(db, embedding_provider)
    compressor = ContextCompressor(llm)
    return ConcreteRAGService(paper_repo, retriever, compressor)

async def get_citation_verifier(llm: LLMProvider = Depends(get_llm_provider)) -> CitationVerifier:
    return CitationVerifier(llm)

async def get_conversation_service(
    conv_repo: SQLAlchemyConversationRepository = Depends(get_conv_repo),
    rag_service: ConcreteRAGService = Depends(get_rag_service),
    llm: LLMProvider = Depends(get_llm_provider),
    verifier: CitationVerifier = Depends(get_citation_verifier)
) -> ConcreteConversationService:
    return ConcreteConversationService(conv_repo, rag_service, llm, verifier)

async def get_paper_ingestion_service(
    paper_repo: SQLAlchemyPaperRepository = Depends(get_paper_repo),
    job_repo: SQLAlchemyJobRepository = Depends(get_job_repo)
) -> ConcretePaperIngestionService:
    return ConcretePaperIngestionService(paper_repo, job_repo)

async def get_research_agent_service(
    job_repo: SQLAlchemyJobRepository = Depends(get_job_repo)
) -> ConcreteResearchAgentService:
    return ConcreteResearchAgentService(job_repo)

async def get_job_service(
    job_repo: SQLAlchemyJobRepository = Depends(get_job_repo)
) -> ConcreteJobService:
    return ConcreteJobService(job_repo)
