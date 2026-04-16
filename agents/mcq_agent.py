"""MCQ Agent — generates multiple-choice questions from financial documents."""
import json

from crewai import Agent, Task, Crew, Process
from pydantic import BaseModel, Field

from agents.llm_client import get_ollama_llm
from agents.tools import DocumentSearchTool


class MCQOption(BaseModel):
    A: str
    B: str
    C: str
    D: str


class MCQ(BaseModel):
    question: str
    options: MCQOption
    correct_answer: str = Field(pattern=r"^[A-D]$")
    explanation: str
    difficulty: str = Field(default="Medium", pattern=r"^(Easy|Medium|Hard)$")
    topic: str = ""


def create_mcq_agent(search_tool: DocumentSearchTool) -> Agent:
    return Agent(
        role="Financial Education Specialist",
        goal=(
            "Generate high-quality multiple-choice questions that test deep understanding "
            "of financial documents. Each question has 4 options (A-D), one correct answer, "
            "an explanation, and a difficulty rating."
        ),
        backstory=(
            "You create rigorous MCQs for financial analyst training programs. "
            "Each question has exactly one clearly correct answer and three plausible "
            "distractors. You base every question on specific facts from the documents. "
            "You always return valid JSON."
        ),
        tools=[search_tool],
        llm=get_ollama_llm(temperature=0.4),
        max_iter=3,
        verbose=True,
    )


def run_mcq(
    num_questions: int,
    search_tool: DocumentSearchTool,
    topic: str = "",
    show_answers: bool = True,
) -> str:
    """Generate MCQs and return formatted output."""
    agent = create_mcq_agent(search_tool)
    topic_hint = f" focusing on: {topic}" if topic else ""
    task = Task(
        description=(
            f"Generate {num_questions} multiple choice questions{topic_hint} "
            "using the document search tool.\n\n"
            "Rules:\n"
            "- Each question has exactly 4 options (A, B, C, D)\n"
            "- Only one option is correct\n"
            "- Include a difficulty rating (Easy/Medium/Hard)\n"
            "- Include an explanation for the correct answer\n"
            "- Include a topic tag\n"
            "- Return ONLY a valid JSON array — no extra text\n\n"
            "JSON format:\n"
            '[{"question": "...", "options": {"A": "...", "B": "...", "C": "...", "D": "..."}, '
            '"correct_answer": "A", "explanation": "...", "difficulty": "Medium", "topic": "..."}]'
        ),
        expected_output=(
            f"A valid JSON array of {num_questions} MCQ objects."
        ),
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()
    raw = str(result)

    # Try to parse and validate
    try:
        mcqs = json.loads(raw)
        validated = [MCQ(**q) for q in mcqs]
        lines = []
        for i, q in enumerate(validated, 1):
            lines.append(f"\nQ{i}. [{q.difficulty}] {q.question}")
            for letter in ["A", "B", "C", "D"]:
                opt = getattr(q.options, letter)
                if show_answers and letter == q.correct_answer:
                    lines.append(f"  {letter}) {opt}  ✓")
                else:
                    lines.append(f"  {letter}) {opt}")
            if show_answers:
                lines.append(f"  → {q.explanation}")
            if q.topic:
                lines.append(f"  Topic: {q.topic}")
        return "\n".join(lines)
    except (json.JSONDecodeError, Exception):
        return raw
