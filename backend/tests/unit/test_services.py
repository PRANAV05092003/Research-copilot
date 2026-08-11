import uuid
from unittest.mock import AsyncMock

import pytest

from app.models import Conversation, Job, Paper
from app.services.interfaces import (
    ConcreteConversationService,
    ConcretePaperIngestionService,
    ConcreteRAGService,
)


@pytest.fixture
def mock_paper_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_job_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_conv_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_retriever():
    retriever = AsyncMock()
    retriever.retrieve.return_value = [{"chunk_id": "1", "text": "Raw text 1", "score": 0.9}]
    return retriever


@pytest.fixture
def mock_compressor():
    compressor = AsyncMock()
    compressor.compress.return_value = [
        {"chunk_id": "1", "text": "Compressed text 1", "score": 0.9}
    ]
    return compressor


@pytest.fixture
def mock_rag_service():
    rag = AsyncMock()
    rag.hybrid_search.return_value = [{"chunk_id": "1", "text": "Compressed text 1", "score": 0.9}]
    return rag


@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    llm.generate.return_value = "This is a mock answer."
    llm.generate_json.return_value = {"status": "pass", "search_queries": ["query1"]}
    return llm


@pytest.fixture
def mock_verifier():
    verifier = AsyncMock()
    verifier.verify_citation.return_value = {"score": 1.0, "verdict": "verified"}
    return verifier


@pytest.mark.asyncio
async def test_paper_ingestion_service(mock_paper_repo, mock_job_repo):
    service = ConcretePaperIngestionService(mock_paper_repo, mock_job_repo)
    user_id = uuid.uuid4()
    workspace_id = uuid.uuid4()

    mock_paper_repo.create.return_value = Paper(id=uuid.uuid4(), title="test.pdf")
    job_id = uuid.uuid4()
    mock_job_repo.create.return_value = Job(id=job_id)

    returned_job_id = await service.enqueue_paper(b"dummy data", "test.pdf", user_id, workspace_id)

    assert returned_job_id == job_id
    mock_paper_repo.create.assert_called_once()
    mock_job_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_rag_service_hybrid_search(mock_paper_repo, mock_retriever, mock_compressor):
    service = ConcreteRAGService(mock_paper_repo, mock_retriever, mock_compressor)
    workspace_id = uuid.uuid4()

    results = await service.hybrid_search("test query", workspace_id)

    assert len(results) == 1
    assert results[0]["score"] == 0.9
    assert "Compressed text 1" in results[0]["text"]
    mock_retriever.retrieve.assert_called_once()
    mock_compressor.compress.assert_called_once()


@pytest.mark.asyncio
async def test_conversation_service_create(
    mock_conv_repo, mock_rag_service, mock_llm, mock_verifier
):
    service = ConcreteConversationService(mock_conv_repo, mock_rag_service, mock_llm, mock_verifier)
    user_id = uuid.uuid4()
    workspace_id = uuid.uuid4()

    mock_conv_repo.create.return_value = Conversation(id=uuid.uuid4(), title="Test Conv")

    conv = await service.create_conversation("Test Conv", user_id, workspace_id, "chat")

    assert conv.title == "Test Conv"
    mock_conv_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_conversation_service_send_message(
    mock_conv_repo, mock_rag_service, mock_llm, mock_verifier
):
    service = ConcreteConversationService(mock_conv_repo, mock_rag_service, mock_llm, mock_verifier)
    conv_id = uuid.uuid4()

    mock_conv = Conversation(id=conv_id, workspace_id=uuid.uuid4(), title="Test Conv", messages=[])
    mock_conv_repo.get_by_id.return_value = mock_conv

    msg = await service.send_message(conv_id, "Hello")
    assert msg.role == "assistant"
    assert msg.content == "This is a mock answer."
    assert msg.confidence == 1.0
    mock_rag_service.hybrid_search.assert_called()
    mock_llm.generate.assert_called()
