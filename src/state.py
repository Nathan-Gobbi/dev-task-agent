"""Shared state used by the LangGraph workflow."""

from typing import TypedDict


class AgentState(TypedDict):
    task: str
    analysis: str
    plan: str
    review: str
    approved: bool
    revision_count: int
    max_revisions: int
    revision_limit_reached: bool
