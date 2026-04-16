"""Q&A Agent — answers specific financial questions with citations."""
from crewai import Agent, Task, Crew, Process

from agents.llm_client import get_ollama_llm
from agents.tools import DocumentSearchTool


def create_qa_agent(search_tool: DocumentSearchTool) -> Agent:
    return Agent(
        role="Financial Q&A Analyst",
        goal=(
            "Answer specific questions about financial documents with precision. "
            "Always cite the source document and page number. Use exact figures."
        ),
        backstory=(
            "You are an expert financial analyst with deep knowledge of SEC filings, "
            "earnings reports, balance sheets, and income statements. "
            "You always ground your answers in the retrieved document content "
            "and never fabricate figures."
        ),
        tools=[search_tool],
        llm=get_ollama_llm(temperature=0.1),
        max_iter=3,
        verbose=True,
    )


def run_qa(question: str, search_tool: DocumentSearchTool, context: str = "") -> str:
    """Run the Q&A agent on a single question and return the answer."""
    agent = create_qa_agent(search_tool)
    task = Task(
        description=(
            f"Answer the following financial question using the document search tool.\n\n"
            f"Question: {question}\n\n"
            + (f"Additional context from conversation:\n{context}\n\n" if context else "")
            + "Provide a precise answer with specific numbers and source citations."
        ),
        expected_output=(
            "A clear, precise answer citing source documents and page numbers. "
            "Include specific figures, percentages, and trends."
        ),
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()
    return str(result)
