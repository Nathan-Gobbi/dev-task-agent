"""Nodes that analyze, plan, and review a development task."""

from typing import Protocol

from pydantic import BaseModel, Field

from src.state import AgentState


class ChatModel(Protocol):
    """Small interface needed by the nodes and their test doubles."""

    def invoke(self, input: str) -> object: ...

    def with_structured_output(self, schema: type[BaseModel]) -> object: ...


class PlanReview(BaseModel):
    """Reliable, structured result produced by the reviewer."""

    approved: bool = Field(description="Whether the plan is ready to use")
    feedback: str = Field(description="Short explanation or improvement request")


def _text(response: object) -> str:
    content = getattr(response, "content", response)
    return str(content).strip()


def analyze_task(state: AgentState, llm: ChatModel) -> dict[str, str]:
    prompt = f"""Analyze the development task below briefly and objectively.
Identify its goal, main requirements, mentioned technologies, and important points.

Task:
{state['task']}
"""
    return {"analysis": _text(llm.invoke(prompt))}


def generate_plan(state: AgentState, llm: ChatModel) -> dict[str, str]:
    feedback = state.get("review", "")
    feedback_section = (
        f"\nReviewer feedback to address:\n{feedback}\n" if feedback else ""
    )
    prompt = f"""Create a practical, concise technical implementation plan in numbered steps.
Avoid unnecessary complexity.

Original task:
{state['task']}

Task analysis:
{state['analysis']}
{feedback_section}
Return only the plan.
"""
    return {"plan": _text(llm.invoke(prompt))}


def review_plan(state: AgentState, llm: ChatModel) -> dict[str, object]:
    prompt = f"""Review whether this plan fulfills the task, has coherent steps,
covers essential points, and avoids unnecessary complexity.

Task:
{state['task']}

Plan:
{state['plan']}
"""
    reviewer = llm.with_structured_output(PlanReview)
    result = reviewer.invoke(prompt)
    if not isinstance(result, PlanReview):
        result = PlanReview.model_validate(result)

    revision_count = state.get("revision_count", 0) + 1
    max_revisions = state.get("max_revisions", 2)
    limit_reached = not result.approved and revision_count >= max_revisions

    return {
        "approved": result.approved,
        "review": result.feedback,
        "revision_count": revision_count,
        "revision_limit_reached": limit_reached,
    }
