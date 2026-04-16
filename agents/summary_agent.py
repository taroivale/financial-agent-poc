"""Summary Agent — produces structured executive summaries."""
from crewai import Agent, Task, Crew, Process

from agents.llm_client import get_ollama_llm
from agents.tools import DocumentSearchTool


def create_summary_agent(search_tool: DocumentSearchTool) -> Agent:
    return Agent(
        role="Senior Financial Analyst",
        goal=(
            "Generate concise, structured executive summaries from financial documents. "
            "Highlight key metrics, trends, risks, and forward-looking recommendations."
        ),
        backstory=(
            "You are a senior financial analyst who distills complex financial documents "
            "into executive-ready briefings. You structure every summary with: "
            "Overview, Key Findings, Trends, Risks, and Recommendations."
        ),
        tools=[search_tool],
        llm=get_ollama_llm(temperature=0.3),
        max_iter=3,
        verbose=True,
    )


def run_summary(topic: str, search_tool: DocumentSearchTool, context: str = "") -> str:
    """Run the summary agent and return a structured executive summary."""
    agent = create_summary_agent(search_tool)
    description = (
        f"Generate an executive summary for: {topic}\n\n"
        "Search the documents and produce a structured summary with these sections:\n"
        "## Overview\n## Key Findings\n## Trends\n## Risks\n## Recommendations\n\n"
        "Use specific figures and cite sources."
    )
    if context:
        description += f"\n\nAdditional context:\n{context}"

    task = Task(
        description=description,
        expected_output=(
            "A markdown-formatted executive summary with five sections: "
            "Overview, Key Findings, Trends, Risks, and Recommendations. "
            "Use bullet points and cite specific figures."
        ),
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()
    return str(result)


def run_insights(topic: str, search_tool: DocumentSearchTool) -> str:
    """Generate focused insights on a specific topic using RAG retrieval."""
    agent = create_summary_agent(search_tool)
    task = Task(
        description=(
            f"Analyze the following topic in depth using the document search tool: {topic}\n\n"
            "Provide focused insights with specific data points, comparisons, and trends."
        ),
        expected_output=(
            "A focused analysis with specific data points, trends, and actionable insights. "
            "Cite sources and include exact figures."
        ),
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()
    return str(result)
