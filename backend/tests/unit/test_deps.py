import pytest

from app.ai.providers.mock import HashEmbeddingProvider, MockLLMProvider
from app.ai.providers.openai import OpenAILLMProvider
from app.ai.providers.sentence_transformers import SentenceTransformersEmbeddingProvider
from app.api.deps import get_embedding_provider, get_llm_provider
from app.config import settings


@pytest.mark.asyncio
async def test_get_llm_provider_mock():
    original = settings.LLM_PROVIDER
    settings.LLM_PROVIDER = "mock"

    provider = await get_llm_provider()
    assert isinstance(provider, MockLLMProvider)

    settings.LLM_PROVIDER = original


@pytest.mark.asyncio
async def test_get_llm_provider_openai(monkeypatch):
    original = settings.LLM_PROVIDER
    settings.LLM_PROVIDER = "openai"
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    settings.OPENAI_API_KEY = "test-key"

    provider = await get_llm_provider()
    assert isinstance(provider, OpenAILLMProvider)

    settings.LLM_PROVIDER = original
    settings.OPENAI_API_KEY = None


@pytest.mark.asyncio
async def test_get_embedding_provider_mock():
    original = settings.EMBEDDING_PROVIDER
    settings.EMBEDDING_PROVIDER = "mock"

    provider = await get_embedding_provider()
    assert isinstance(provider, HashEmbeddingProvider)

    settings.EMBEDDING_PROVIDER = original


@pytest.mark.asyncio
async def test_get_embedding_provider_sentence_transformers():
    # sentence transformers takes time and downloads models if not present, so we will just test it conditionally or mock the import
    # we can mock the class internally
    original = settings.EMBEDDING_PROVIDER
    settings.EMBEDDING_PROVIDER = "sentence-transformers"

    # We will instantiate it, it will use all-MiniLM-L6-v2 which might be cached or downloaded
    # To avoid downloading in tests, we can skip or just test the instance type
    # If the model is not present, it will download it. For strict CI, we should mock the model.
    # Let's mock the SentenceTransformersEmbeddingProvider __init__

    import unittest.mock

    with unittest.mock.patch(
        "app.ai.providers.sentence_transformers.SentenceTransformersEmbeddingProvider.__init__",
        return_value=None,
    ):
        provider = await get_embedding_provider()
        assert isinstance(provider, SentenceTransformersEmbeddingProvider)

    settings.EMBEDDING_PROVIDER = original
