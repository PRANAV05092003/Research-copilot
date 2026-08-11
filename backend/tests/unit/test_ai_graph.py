from unittest.mock import AsyncMock

import pytest

from app.ai.agents.graph import build_research_graph
from app.ai.agents.nodes import AgentNodes


@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    # Mock specific return values if possible or just use a generic json
    llm.generate_json.side_effect = [
        {"search_queries": ["query1"]}, # Planner
        {"status": "pass", "feedback": "good"} # Critic
    ]
    llm.generate.return_value = "Draft answer"
    return llm

@pytest.fixture
def mock_rag():
    rag = AsyncMock()
    rag.hybrid_search.return_value = [{"chunk_id": "1", "text": "mock text"}]
    return rag

@pytest.fixture
def mock_verifier():
    verifier = AsyncMock()
    verifier.verify_citation.return_value = {"verdict": "verified", "score": 1.0}
    return verifier

@pytest.mark.asyncio
async def test_langgraph_nodes_and_graph(mock_llm, mock_rag, mock_verifier):
    nodes = AgentNodes(mock_llm, mock_rag, mock_verifier)
    graph = build_research_graph(nodes)
    
    initial_state = {
        "query": "test query",
        "iterations": 0,
        "context": [],
        "citations": []
    }
    
    # Run the graph
    final_state = await graph.ainvoke(initial_state)
    
    assert final_state["final_answer"] == "Draft answer"
    assert final_state["iterations"] == 1
    assert len(final_state["citations"]) == 1
    assert final_state["citations"][0]["score"] == 1.0
    
    mock_llm.generate_json.assert_called()
    mock_llm.generate.assert_called()
    mock_rag.hybrid_search.assert_called_once()
    mock_verifier.verify_citation.assert_called_once()
