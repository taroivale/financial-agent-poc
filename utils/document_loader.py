"""Legacy document loading utilities.

Thin wrappers around the RAG pipeline loaders for backward compatibility
and standalone use (e.g., loading documents without building a vector store).
"""
from pathlib import Path

from langchain_core.documents import Document

from utils.rag_pipeline import load_pdf, load_csv


def load_documents_from_directory(directory: str | Path) -> list[Document]:
    """Load all PDFs and CSVs from a directory."""
    directory = Path(directory)
    docs: list[Document] = []
    for f in sorted(directory.iterdir()):
        if f.suffix.lower() == ".pdf":
            docs.extend(load_pdf(f))
        elif f.suffix.lower() == ".csv":
            docs.extend(load_csv(f))
    return docs
