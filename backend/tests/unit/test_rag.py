import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.ai.rag.compressor import ContextCompressor
from app.ai.rag.retriever import PgVectorRetriever
from app.models import Paper, PaperChunk


@pytest.fixture
def mock_embedding_provider():
    provider = AsyncMock()
    provider.embed_documents.return_value = [[0.1, 0.2, 0.3]]
    return provider


@pytest.fixture
def mock_llm_provider():
    provider = AsyncMock()
    provider.generate.return_value = "Compressed summary."
    return provider


@pytest.fixture
def mock_session():
    session = AsyncMock()

    # Mocking the result of session.execute()
    mock_result = MagicMock()

    chunk = PaperChunk(
        id=uuid.uuid4(), text="Raw chunk text", page_number=1, embedding=[0.1, 0.2, 0.3]
    )
    paper = Paper(id=uuid.uuid4(), title="Test Paper")

    mock_result.all.return_value = [(chunk, paper)]
    session.execute.return_value = mock_result
    return session


@pytest.mark.asyncio
async def test_pgvector_retriever(mock_session, mock_embedding_provider):
    retriever = PgVectorRetriever(mock_session, mock_embedding_provider)

    workspace_id = uuid.uuid4()
    results = await retriever.retrieve("test query", top_k=5, workspace_id=workspace_id)

    assert len(results) == 1
    assert results[0]["text"] == "Raw chunk text"
    assert results[0]["paper_title"] == "Test Paper"
    mock_embedding_provider.embed_documents.assert_called_once_with(["test query"])
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_context_compressor(mock_llm_provider):
    compressor = ContextCompressor(mock_llm_provider)

    chunks = [{"text": "Very long text that is mostly irrelevant."}]
    compressed = await compressor.compress("What is the main finding?", chunks)

    assert len(compressed) == 1
    assert compressed[0]["text"] == "Compressed summary."
    mock_llm_provider.generate.assert_called_once()


@pytest.mark.asyncio
async def test_context_compressor_no_relevance(mock_llm_provider):
    mock_llm_provider.generate.return_value = "NO_RELEVANCE"
    compressor = ContextCompressor(mock_llm_provider)

    chunks = [{"text": "Irrelevant stuff."}]
    compressed = await compressor.compress("What is the main finding?", chunks)

    assert len(compressed) == 0
