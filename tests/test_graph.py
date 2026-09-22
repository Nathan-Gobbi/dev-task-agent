from dataclasses import dataclass

from src.graph import build_graph, route_review
from src.nodes import PlanReview


@dataclass
class FakeMessage:
    content: str


class FakeStructuredModel:
    def __init__(self, reviews: list[PlanReview]) -> None:
        self.reviews = reviews

    def invoke(self, _prompt: str) -> PlanReview:
        return self.reviews.pop(0)


class FakeLLM:
    def __init__(self, approvals: list[bool]) -> None:
        self.reviews = [
            PlanReview(approved=value, feedback="Plano adequado." if value else "Adicione testes.")
            for value in approvals
        ]
        self.invocation_count = 0

    def invoke(self, _prompt: str) -> FakeMessage:
        self.invocation_count += 1
        if self.invocation_count == 1:
            return FakeMessage("Objetivo e requisitos analisados.")
        return FakeMessage(f"{self.invocation_count - 1}. Plano técnico revisado.")

    def with_structured_output(self, _schema: type[PlanReview]) -> FakeStructuredModel:
        return FakeStructuredModel(self.reviews)


def make_state(**changes):
    state = {
        "task": "Criar uma API",
        "analysis": "",
        "plan": "",
        "review": "",
        "approved": False,
        "revision_count": 0,
        "max_revisions": 2,
        "revision_limit_reached": False,
    }
    state.update(changes)
    return state


def test_route_review_ends_when_approved():
    assert route_review(make_state(approved=True)) == "__end__"


def test_route_review_retries_when_rejected():
    assert route_review(make_state()) == "generate_plan"


def test_graph_stops_at_maximum_revisions():
    result = build_graph(FakeLLM([False, False])).invoke(make_state())

    assert result["approved"] is False
    assert result["revision_count"] == 2
    assert result["revision_limit_reached"] is True


def test_graph_runs_with_fake_llm_and_approves_revised_plan():
    fake_llm = FakeLLM([False, True])

    result = build_graph(fake_llm).invoke(make_state())

    assert result["approved"] is True
    assert result["revision_count"] == 2
    assert result["revision_limit_reached"] is False
    assert fake_llm.invocation_count == 3
