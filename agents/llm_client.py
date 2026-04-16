"""CrewAI-compatible Ollama LLM config."""
import os

from crewai import LLM

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")


def get_ollama_llm(temperature: float = 0.2) -> LLM:
    """Returns a CrewAI LLM using Ollama via LiteLLM."""
    return LLM(
        model=f"ollama/{OLLAMA_MODEL}",
        base_url=OLLAMA_BASE_URL,
        temperature=temperature,
    )
