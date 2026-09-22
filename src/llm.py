"""Central configuration for the local Ollama model."""

from langchain_ollama import ChatOllama

MODEL_NAME = "gpt-oss:20b"


def create_llm() -> ChatOllama:
    """Create the single chat model used by the workflow."""
    return ChatOllama(model=MODEL_NAME, temperature=0)
