import abc
import hashlib
import uuid
from typing import Any

from app.ai.agents.graph import build_research_graph
from app.ai.agents.nodes import AgentNodes
from app.ai.providers.base import LLMProvider
from app.ai.rag.compressor import ContextCompressor
from app.ai.rag.retriever import BaseRetriever
from app.ai.verification.citation_verifier import CitationVerifier
from app.db.repositories import ConversationRepository, JobRepository, PaperRepository
from app.models import Conversation, Job, Message, Paper


class PaperIngestionService(abc.ABC):
    @abc.abstractmethod
    async def enqueue_paper(
        self, file_bytes: bytes, filename: str, user_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> uuid.UUID:
        pass


class RAGService(abc.ABC):
    @abc.abstractmethod
    async def hybrid_search(
        self, query: str, workspace_id: uuid.UUID, top_k: int = 10
    ) -> list[dict[str, Any]]:
        pass


class ResearchAgentService(abc.ABC):
    @abc.abstractmethod
    async def generate_deep_review(
        self, topic: str, user_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> uuid.UUID:
        pass


class ConversationService(abc.ABC):
    @abc.abstractmethod
    async def create_conversation(
        self, title: str, user_id: uuid.UUID, workspace_id: uuid.UUID, mode: str
    ) -> Conversation:
        pass

    @abc.abstractmethod
    async def send_message(self, conv_id: uuid.UUID, content: str) -> Message:
        pass


class JobService(abc.ABC):
    @abc.abstractmethod
    async def get_job_status(self, job_id: uuid.UUID) -> Job | None:
        pass


class ConcretePaperIngestionService(PaperIngestionService):
    def __init__(self, paper_repo: PaperRepository, job_repo: JobRepository):
        self.paper_repo = paper_repo
        self.job_repo = job_repo

    async def enqueue_paper(
        self, file_bytes: bytes, filename: str, user_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> uuid.UUID:
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        paper = Paper(
            workspace_id=workspace_id,
            title=filename,
            file_hash=file_hash,
            created_by=user_id,
            status="pending",
        )
        paper = await self.paper_repo.create(paper)

        job = Job(type="ingest", ref_id=paper.id, owner_id=user_id, status="queued")
        job = await self.job_repo.create(job)

        import os

        from arq import create_pool
        from arq.connections import RedisSettings

        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        pool = await create_pool(RedisSettings.from_dsn(redis_url))
        await pool.enqueue_job("ingest_paper_task", paper.id, file_bytes, user_id, workspace_id)

        return job.id


class ConcreteRAGService(RAGService):
    def __init__(
        self, paper_repo: PaperRepository, retriever: BaseRetriever, compressor: ContextCompressor
    ):
        self.paper_repo = paper_repo
        self.retriever = retriever
        self.compressor = compressor

    async def hybrid_search(
        self, query: str, workspace_id: uuid.UUID, top_k: int = 10
    ) -> list[dict[str, Any]]:
        # 1. Retrieve raw chunks
        raw_chunks = await self.retriever.retrieve(
            query=query, top_k=top_k * 2, workspace_id=workspace_id
        )

        # 2. Compress context
        compressed = await self.compressor.compress(query, raw_chunks)

        # 3. Limit to top_k after compression filtering
        return compressed[:top_k]


class ConcreteResearchAgentService(ResearchAgentService):
    def __init__(self, job_repo: JobRepository):
        self.job_repo = job_repo

    async def generate_deep_review(
        self, topic: str, user_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> uuid.UUID:
        job = Job(
            type="deep_research",
            ref_id=workspace_id,  # Link to workspace since it's a general review
            owner_id=user_id,
            status="queued",
            result={"topic": topic},
        )
        job = await self.job_repo.create(job)

        import os

        from arq import create_pool
        from arq.connections import RedisSettings

        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        pool = await create_pool(RedisSettings.from_dsn(redis_url))
        await pool.enqueue_job("deep_research_task", job.id, topic, workspace_id)

        return job.id


class ConcreteConversationService(ConversationService):
    def __init__(
        self,
        conv_repo: ConversationRepository,
        rag_service: RAGService,
        llm: LLMProvider,
        verifier: CitationVerifier,
    ):
        self.conv_repo = conv_repo
        self.rag_service = rag_service
        self.llm = llm
        self.verifier = verifier

        # Initialize LangGraph
        self.nodes = AgentNodes(llm, rag_service, verifier)
        self.graph = build_research_graph(self.nodes)

    async def create_conversation(
        self, title: str, user_id: uuid.UUID, workspace_id: uuid.UUID, mode: str
    ) -> Conversation:
        conv = Conversation(workspace_id=workspace_id, user_id=user_id, title=title, mode=mode)
        conv = await self.conv_repo.create(conv)
        return conv

    async def send_message(self, conv_id: uuid.UUID, content: str) -> Message:
        user_msg = Message(conversation_id=conv_id, role="user", content=content)
        await self.conv_repo.add_message(user_msg)

        conv = await self.conv_repo.get_by_id(conv_id)
        workspace_id = conv.workspace_id if conv else uuid.uuid4()

        # Prepare initial state for LangGraph
        initial_state = {
            "query": content,
            "filters": {"workspace_id": workspace_id},
            "iterations": 0,
            "context": [],
            "citations": [],
        }

        # Execute LangGraph pipeline
        final_state = await self.graph.ainvoke(initial_state)

        draft_answer = final_state.get("final_answer", "")
        citations = final_state.get("citations", [])

        # Calculate confidence
        total_score = sum(c.get("score", 0.0) for c in citations)
        confidence = (total_score / len(citations)) if citations else 1.0

        assistant_msg = Message(
            conversation_id=conv_id,
            role="assistant",
            content=draft_answer,
            confidence=confidence,
            agent_trace={"iterations": final_state.get("iterations")},
        )
        await self.conv_repo.add_message(assistant_msg)
        return assistant_msg


class ConcreteJobService(JobService):
    def __init__(self, job_repo: JobRepository):
        self.job_repo = job_repo

    async def get_job_status(self, job_id: uuid.UUID) -> Job | None:
        return await self.job_repo.get_by_id(job_id)
