from typing import Any

from langgraph.graph import END, StateGraph

from app.ai.agents.nodes import AgentNodes
from app.ai.agents.state import AgentState


def should_continue(state: AgentState) -> str:
    """Routing function to decide next steps after critic."""
    if state.get("needs_more_info", False) and state.get("iterations", 0) < 3:
        return "planner"
    return "writer"


def build_research_graph(nodes: AgentNodes) -> Any:
    """Builds and compiles the LangGraph."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planner", nodes.planner_node)
    workflow.add_node("retriever", nodes.retriever_node)
    workflow.add_node("reader", nodes.reader_node)
    workflow.add_node("verifier", nodes.verifier_node)
    workflow.add_node("critic", nodes.critic_node)
    workflow.add_node("writer", nodes.writer_node)

    # Define edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "retriever")
    workflow.add_edge("retriever", "reader")
    workflow.add_edge("reader", "verifier")
    workflow.add_edge("verifier", "critic")

    # Conditional edge
    workflow.add_conditional_edges(
        "critic", should_continue, {"planner": "planner", "writer": "writer"}
    )

    workflow.add_edge("writer", END)

    return workflow.compile()
