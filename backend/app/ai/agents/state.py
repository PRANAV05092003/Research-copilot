import operator
from typing import Annotated, Any, TypedDict


# State for the RAG LangGraph Agent
class AgentState(TypedDict):
    # Current query being processed
    query: str

    # Optional workspace or paper limits
    filters: dict[str, Any] | None

    # Gathered contexts from retrieval
    context: Annotated[list[dict[str, Any]], operator.add]

    # Generated intermediate answer
    draft_answer: str | None

    # Citations generated from draft
    citations: Annotated[list[dict[str, Any]], operator.add]

    # Boolean flag to decide if we need more context
    needs_more_info: bool

    # Critic's feedback
    feedback: str | None

    # Number of iteration loops
    iterations: int

    # Final verified answer
    final_answer: str | None
