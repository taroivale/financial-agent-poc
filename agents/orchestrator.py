"""Orchestrator Agent — classifies user requests and routes to the right agent."""
import json
import re

from crewai import Agent, Task, Crew, Process

from agents.llm_client import get_ollama_llm


CLASSIFY_DESCRIPTION = (
    "Classify the following user message into one of these categories:\n"
    "- 'qa': The user is asking a specific question about financial data\n"
    "- 'summary': The user wants a summary, overview, or executive briefing\n"
    "- 'mcq': The user wants quiz questions or multiple choice questions\n\n"
    "User message: {message}\n\n"
    'Respond with ONLY a JSON object: {{"agent": "qa"|"summary"|"mcq", "detail": "brief reason"}}'
)

# Keyword-based fallback patterns
_PATTERNS = {
    "summary": re.compile(
        r"\b(summar|overview|briefing|executive|highlights?|recap|outline)\b", re.I
    ),
    "mcq": re.compile(
        r"\b(mcq|quiz|multiple.?choice|test\s+me|questions?\s+about|generate.*questions?)\b", re.I
    ),
}


def classify_request(message: str) -> str:
    """Classify a user message into 'qa', 'summary', or 'mcq'.

    Uses LLM classification with a keyword-based fallback.
    """
    # Try LLM classification
    try:
        agent = Agent(
            role="Request Classifier",
            goal="Classify user requests into qa, summary, or mcq categories.",
            backstory="You are a routing assistant that determines intent.",
            llm=get_ollama_llm(temperature=0.0),
            max_iter=1,
            verbose=False,
        )
        task = Task(
            description=CLASSIFY_DESCRIPTION.format(message=message),
            expected_output='A JSON object with "agent" and "detail" keys.',
            agent=agent,
        )
        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
        result = str(crew.kickoff())

        # Extract JSON from result
        match = re.search(r'\{[^}]+\}', result)
        if match:
            parsed = json.loads(match.group())
            agent_type = parsed.get("agent", "").lower()
            if agent_type in ("qa", "summary", "mcq"):
                return agent_type
    except Exception:
        pass

    # Keyword fallback
    for agent_type, pattern in _PATTERNS.items():
        if pattern.search(message):
            return agent_type
    return "qa"
