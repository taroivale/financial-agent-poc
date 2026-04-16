"""
RAG Pipeline — LangChain + ChromaDB.

Loads PDFs and CSVs, splits into chunks, embeds with Ollama,
stores in ChromaDB, and provides a retrieval chain.
"""
import os
import subprocess
from pathlib import Path

import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")

FINANCIAL_PROMPT = ChatPromptTemplate.from_template(
    "You are a senior financial analyst. Use the following retrieved context "
    "to answer the question. Cite specific figures, percentages, and source "
    "documents where possible. If the context does not contain enough "
    "information, say so.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Answer:"
)


def _ensure_model(model: str = OLLAMA_MODEL) -> None:
    """Pull the Ollama model if it isn't already present."""
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=10
        )
        if model in result.stdout:
            return
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    print(f"[rag] Pulling model '{model}' (first run only)...")
    subprocess.run(["ollama", "pull", model], check=False)


def load_pdf(path: str | Path) -> list[Document]:
    """Load a PDF and return one LangChain Document per page."""
    from pypdf import PdfReader

    path = Path(path)
    reader = PdfReader(str(path))
    docs = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            docs.append(Document(
                page_content=text,
                metadata={"source": path.name, "page": i + 1},
            ))
    print(f"[rag] Loaded {len(docs)} pages from '{path.name}'")
    return docs


def load_csv(path: str | Path) -> list[Document]:
    """Load a CSV — emit a summary doc plus one doc per row."""
    path = Path(path)
    df = pd.read_csv(path)
    docs = []

    # Summary statistics document
    stats = df.describe(include="all").to_string()
    docs.append(Document(
        page_content=f"Summary statistics for {path.name}:\n{stats}",
        metadata={"source": path.name, "type": "stats"},
    ))

    # One document per row
    for idx, row in df.iterrows():
        text = " | ".join(f"{col}: {val}" for col, val in row.items() if pd.notna(val))
        if text.strip():
            docs.append(Document(
                page_content=text,
                metadata={"source": path.name, "row": int(idx)},
            ))
    print(f"[rag] Loaded {len(docs)} documents from '{path.name}'")
    return docs


def load_documents(paths: list[str | Path]) -> list[Document]:
    """Load a mix of PDFs and CSVs from the given paths."""
    all_docs: list[Document] = []
    for p in paths:
        p = Path(p)
        if not p.exists():
            print(f"[rag] Warning: '{p}' not found, skipping.")
            continue
        if p.suffix.lower() == ".pdf":
            all_docs.extend(load_pdf(p))
        elif p.suffix.lower() == ".csv":
            all_docs.extend(load_csv(p))
        else:
            print(f"[rag] Skipping unsupported file: {p.name}")
    return all_docs


def _format_docs(docs: list[Document]) -> str:
    """Format retrieved documents into a single context string."""
    return "\n\n".join(doc.page_content for doc in docs)


class RAGPipeline:
    """End-to-end RAG pipeline: ingest → embed → retrieve → answer."""

    def __init__(self, model: str = OLLAMA_MODEL, persist_dir: str = CHROMA_PERSIST_DIR):
        self.model = model
        self.persist_dir = persist_dir
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        self._embeddings = OllamaEmbeddings(
            model=self.model, base_url=OLLAMA_BASE_URL
        )
        self._vectorstore: Chroma | None = None
        self._chain = None
        self._loaded_sources: list[str] = []

    # ── Ingestion ─────────────────────────────────────────────────────────

    def ingest(self, paths: list[str | Path]) -> int:
        """Load documents, chunk, embed, and store in ChromaDB."""
        _ensure_model(self.model)
        docs = load_documents(paths)
        if not docs:
            print("[rag] No documents to ingest.")
            return 0

        chunks = self._splitter.split_documents(docs)
        print(f"[rag] {len(docs)} documents → {len(chunks)} chunks")

        self._vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self._embeddings,
            persist_directory=self.persist_dir,
        )
        self._loaded_sources = list({d.metadata.get("source", "?") for d in docs})
        self._chain = None  # rebuild on next query
        print(f"[rag] Vector store saved to '{self.persist_dir}'")
        return len(chunks)

    def load_existing(self) -> None:
        """Load a previously persisted ChromaDB vector store."""
        if not Path(self.persist_dir).exists():
            raise FileNotFoundError(
                f"No vector store at '{self.persist_dir}'. Ingest documents first."
            )
        self._vectorstore = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self._embeddings,
        )

    # ── Retrieval ─────────────────────────────────────────────────────────

    def retrieve(self, query: str, k: int = 5) -> list[Document]:
        """Return the top-k most relevant chunks for a query."""
        if self._vectorstore is None:
            self.load_existing()
        return self._vectorstore.similarity_search(query, k=k)

    def retrieve_text(self, query: str, k: int = 5) -> str:
        """Return retrieved chunks as a single formatted string."""
        docs = self.retrieve(query, k=k)
        parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page", "")
            header = f"[{i}] {source}" + (f" (p.{page})" if page else "")
            parts.append(f"{header}\n{doc.page_content}")
        return "\n\n---\n\n".join(parts)

    # ── QA Chain ──────────────────────────────────────────────────────────

    def _build_chain(self):
        """Build a retrieval chain using LCEL (LangChain Expression Language)."""
        if self._vectorstore is None:
            self.load_existing()

        llm = ChatOllama(model=self.model, base_url=OLLAMA_BASE_URL, temperature=0.2)
        retriever = self._vectorstore.as_retriever(search_kwargs={"k": 5})

        self._chain = (
            {"context": retriever | _format_docs, "question": RunnablePassthrough()}
            | FINANCIAL_PROMPT
            | llm
            | StrOutputParser()
        )

    def query(self, question: str) -> str:
        """Answer a question using the RAG pipeline."""
        if self._chain is None:
            self._build_chain()
        return self._chain.invoke(question)

    # ── Utility ───────────────────────────────────────────────────────────

    @property
    def sources(self) -> list[str]:
        return list(self._loaded_sources)
