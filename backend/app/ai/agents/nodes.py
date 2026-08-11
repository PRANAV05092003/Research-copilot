import uuid
from typing import TYPE_CHECKING, Any

from app.ai.agents.prompts import CRITIC_PROMPT, PLANNER_PROMPT, READER_PROMPT
from app.ai.agents.state import AgentState
from app.ai.providers.base import LLMProvider
from app.ai.verification.citation_verifier import CitationVerifier

if TYPE_CHECKING:
    from app.services.interfaces import RAGService


class AgentNodes:
    def __init__(self, llm: LLMProvider, rag_service: "RAGService", verifier: CitationVerifier):
        self.llm = llm
        self.rag_service = rag_service
        self.verifier = verifier

    async def planner_node(self, state: AgentState) -> dict[str, Any]:
        """Analyzes query and creates a search strategy."""
        prompt = PLANNER_PROMPT.substitute(query=state["query"])
        response = await self.llm.generate_json(prompt=prompt, system="You are a planning agent.")
        response.get("search_queries", [state["query"]])
        # We can store the planned queries in state if we had a field for it,
        # but for now we just return them mapped to context fetching.
        # However, to keep state simple, we will just pass the main query to the retriever.
        return {"iterations": state.get("iterations", 0) + 1}

    async def retriever_node(self, state: AgentState) -> dict[str, Any]:
        """Uses the RAG service to fetch and compress contexts."""
        filters = state.get("filters") or {}
        workspace_id = filters.get("workspace_id", uuid.uuid4())  # Fallback for tests

        # We use the RAGService which internally handles PgVector retrieval & context compression
        contexts = await self.rag_service.hybrid_search(state["query"], workspace_id, top_k=5)

        return {"context": contexts}

    async def reader_node(self, state: AgentState) -> dict[str, Any]:
        """Synthesizes the answer with inline citations."""
        contexts = state.get("context") or []
        context_str = "\n\n".join([f"[{c.get('chunk_id')}] {c.get('text')}" for c in contexts])

        prompt = READER_PROMPT.substitute(query=state["query"], contexts=context_str)
        draft = await self.llm.generate(prompt)

        return {"draft_answer": draft}

    async def verifier_node(self, state: AgentState) -> dict[str, Any]:
        """Checks citations against the chunks."""
        draft = state.get("draft_answer") or ""
        contexts = state.get("context") or []

        citations = []
        for ctx in contexts:
            res = await self.verifier.verify_citation(draft, ctx.get("text") or "")
            citations.append(
                {
                    "chunk_id": ctx.get("chunk_id"),
                    "verdict": res.get("verdict"),
                    "score": res.get("score", 0.0),
                    "reasoning": res.get("reasoning"),
                }
            )

        return {"citations": citations}

    async def critic_node(self, state: AgentState) -> dict[str, Any]:
        """Evaluates the draft and decides if iteration is needed."""
        draft = state.get("draft_answer", "")
        contexts = state.get("context", [])
        context_str = "\n\n".join([f"[{c.get('chunk_id')}] {c.get('text')}" for c in contexts])

        prompt = CRITIC_PROMPT.substitute(query=state["query"], draft=draft, contexts=context_str)
        eval_res = await self.llm.generate_json(prompt=prompt, system="You are an academic critic.")

        status = eval_res.get("status", "pass")
        needs_more_info = status != "pass"

        return {"feedback": eval_res.get("feedback", ""), "needs_more_info": needs_more_info}

    async def writer_node(self, state: AgentState) -> dict[str, Any]:
        """Finalizes the response based on verified draft."""
        # For simplicity, just promote draft to final. In a real system, we might rewrite based on verifier.
        return {"final_answer": state.get("draft_answer", "")}
