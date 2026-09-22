"""Definition of the Dev Task Agent workflow."""

from typing import Literal

from langgraph.graph import END, START, StateGraph

from src.llm import create_llm
from src.nodes import ChatModel, analyze_task, generate_plan, review_plan
from src.state import AgentState


def route_review(state: AgentState) -> Literal["generate_plan", "__end__"]:
    """Repeat planning only while the plan is rejected and attempts remain."""
    if state["approved"] or state["revision_limit_reached"]:
        return END
    return "generate_plan"


def build_graph(llm: ChatModel | None = None):
    """Build and compile the graph, optionally using a test double."""
    model = llm or create_llm()
    workflow = StateGraph(AgentState)

    workflow.add_node("analyze_task", lambda state: analyze_task(state, model))
    workflow.add_node("generate_plan", lambda state: generate_plan(state, model))
    workflow.add_node("review_plan", lambda state: review_plan(state, model))

    workflow.add_edge(START, "analyze_task")
    workflow.add_edge("analyze_task", "generate_plan")
    workflow.add_edge("generate_plan", "review_plan")
    workflow.add_conditional_edges(
        "review_plan",
        route_review,
        {"generate_plan": "generate_plan", END: END},
    )

    return workflow.compile()
