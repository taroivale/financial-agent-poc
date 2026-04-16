"""CrewAI tools that wrap the LangChain RAG pipeline."""
from crewai.tools import BaseTool

from utils.rag_pipeline import RAGPipeline


class DocumentSearchTool(BaseTool):
    """Search financial documents via the RAG vector store."""

    name: str = "document_search"
    description: str = (
        "Search financial documents (PDFs and CSVs) for relevant information. "
        "Use this tool to find specific financial metrics, risk factors, "
        "statements, or data points. Input should be a specific search query."
    )

    _pipeline: RAGPipeline | None = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, pipeline: RAGPipeline | None = None, **kwargs):
        super().__init__(**kwargs)
        self._pipeline = pipeline

    def _run(self, query: str) -> str:
        if self._pipeline is None:
            self._pipeline = RAGPipeline()
        return self._pipeline.retrieve_text(query, k=5)
