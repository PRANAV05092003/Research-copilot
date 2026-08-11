
import pytest

from app.ai.ingestion.chunker import Chunker
from app.ai.ingestion.metadata_extractor import MetadataExtractor
from app.ai.providers.mock import HashEmbeddingProvider, MockLLMProvider
from app.ai.verification.citation_verifier import CitationVerifier


@pytest.fixture
def mock_llm():
    return MockLLMProvider()

@pytest.fixture
def mock_embedding():
    return HashEmbeddingProvider()

@pytest.mark.asyncio
async def test_mock_llm_generate(mock_llm):
    response = await mock_llm.generate("Hello")
    assert "Mock response" in response

@pytest.mark.asyncio
async def test_mock_embedding_generate(mock_embedding):
    vector = await mock_embedding.embed_query("test text")
    assert len(vector) == 384
    
    # check normalization
    norm = sum(x*x for x in vector) ** 0.5
    assert abs(norm - 1.0) < 1e-5

@pytest.mark.asyncio
async def test_citation_verifier(mock_llm):
    verifier = CitationVerifier(mock_llm)
    # The mock returns 'verified' unless 'mock_unsupported' or 'mock_weak' is in the prompt
    res = await verifier.verify_citation("Some claim", "Supporting chunk")
    assert res["verdict"] == "verified"
    
    res = await verifier.verify_citation("mock_unsupported claim", "Chunk")
    assert res["verdict"] == "unsupported"

    # Test exact quote extraction
    claim = "The accuracy was 95 percent"
    chunk = "We ran the tests. The accuracy was 95 percent. This is good."
    quote = verifier.extract_exact_quote(claim, chunk)
    assert quote == "The accuracy was 95 percent"

def test_metadata_extractor():
    extractor = MetadataExtractor()
    pages = [{"page_number": 1, "text": "Deep Learning for X\nAuthors: A, B\n10.1234/5678\n2023\nAbstract\nThis is the abstract."}]
    
    metadata = extractor.extract(pages)
    assert metadata["title"] == "Deep Learning for X"
    assert metadata["doi"] == "10.1234/5678"
    assert metadata["year"] == 2023
    assert "This is the abstract" in metadata["abstract"]

def test_chunker():
    chunker = Chunker(target_tokens=10, overlap_tokens=2) # Very small for testing
    text = "Sentence one. Sentence two. Sentence three. Sentence four."
    pages = [{"page_number": 1, "text": text}]
    
    chunks = chunker.chunk(pages)
    assert len(chunks) > 1
    assert chunks[0]["page_number"] == 1
    assert "Sentence one" in chunks[0]["text"]
