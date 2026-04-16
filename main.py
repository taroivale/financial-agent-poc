#!/usr/bin/env python3
"""
Financial Document Analyzer — Interactive Multi-Agent Chatbot.

Usage:
    python3 main.py                          # uses sample data
    python3 main.py report.pdf finances.csv  # your own files
    python3 main.py --model mistral          # override model
"""
import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from utils.rag_pipeline import RAGPipeline
from agents.tools import DocumentSearchTool
from agents.orchestrator import classify_request
from agents.qa_agent import run_qa
from agents.summary_agent import run_summary, run_insights
from agents.mcq_agent import run_mcq

console = Console()

# ── Conversation memory ──────────────────────────────────────────────────────

MAX_HISTORY = 50


class ConversationMemory:
    def __init__(self):
        self.turns: list[dict] = []

    def add(self, role: str, content: str, agent: str = ""):
        self.turns.append({
            "role": role,
            "content": content,
            "agent": agent,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        })
        if len(self.turns) > MAX_HISTORY:
            self.turns = self.turns[-MAX_HISTORY:]

    def recent_context(self, n: int = 6) -> str:
        recent = self.turns[-n:] if len(self.turns) > n else self.turns
        lines = []
        for t in recent:
            prefix = "User" if t["role"] == "user" else "Assistant"
            lines.append(f"{prefix}: {t['content'][:200]}")
        return "\n".join(lines)

    def show(self):
        if not self.turns:
            console.print("[dim]No conversation history yet.[/dim]")
            return
        for t in self.turns:
            role = "[bold cyan]You[/bold cyan]" if t["role"] == "user" else "[bold green]Assistant[/bold green]"
            agent_tag = f" [dim]({t['agent']})[/dim]" if t["agent"] else ""
            console.print(f"  [{t['timestamp']}] {role}{agent_tag}: {t['content'][:120]}")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _default_sample_files() -> list[Path]:
    """Return paths to sample data CSVs if they exist."""
    sample_dir = Path(__file__).parent / "sample_data"
    if not sample_dir.exists():
        return []
    return sorted(sample_dir.glob("*.csv")) + sorted(sample_dir.glob("*.pdf"))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Financial Document Analyzer")
    parser.add_argument("files", nargs="*", help="PDF/CSV files to analyze")
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
                        help="Ollama model (default: llama3.1:8b)")
    return parser.parse_args()


# ── Command handlers ─────────────────────────────────────────────────────────

HELP_TEXT = """
[bold]Commands:[/bold]
  [cyan]rag <query>[/cyan]          RAG Pipeline (direct retrieval)
  [cyan]qa <question>[/cyan]        Q&A Agent
  [cyan]summary [topic][/cyan]      Summary Agent (executive summary)
  [cyan]insights <topic>[/cyan]     Summary Agent (focused insights)
  [cyan]mcq [N] [topic][/cyan]      MCQ Agent (with answers)
  [cyan]quiz [N] [topic][/cyan]     MCQ Agent (no answers shown)
  [cyan]docs[/cyan]                 List loaded documents
  [cyan]history[/cyan]              Show conversation history
  [cyan]help[/cyan]                 Show this help

[dim]Or just type a natural language question — it will be auto-routed to the best agent.[/dim]
"""


def handle_command(
    user_input: str,
    pipeline: RAGPipeline,
    search_tool: DocumentSearchTool,
    memory: ConversationMemory,
) -> str:
    """Process a user command and return the response."""
    low = user_input.strip().lower()

    # ── Explicit commands ─────────────────────────────────────────────
    if low.startswith("rag "):
        query = user_input[4:].strip()
        return pipeline.query(query)

    if low.startswith("qa "):
        question = user_input[3:].strip()
        return run_qa(question, search_tool, context=memory.recent_context())

    if low.startswith("summary"):
        topic = user_input[7:].strip() or "overall financial performance"
        return run_summary(topic, search_tool, context=memory.recent_context())

    if low.startswith("insights "):
        topic = user_input[9:].strip()
        return run_insights(topic, search_tool)

    if low.startswith(("mcq", "quiz")):
        is_quiz = low.startswith("quiz")
        parts = user_input.split(maxsplit=2)
        num = 5
        topic = ""
        if len(parts) >= 2:
            try:
                num = int(parts[1])
                topic = parts[2] if len(parts) > 2 else ""
            except ValueError:
                topic = " ".join(parts[1:])
        return run_mcq(num, search_tool, topic=topic, show_answers=not is_quiz)

    if low == "docs":
        sources = pipeline.sources
        if sources:
            return "Loaded documents:\n" + "\n".join(f"  • {s}" for s in sources)
        return "No documents loaded yet."

    if low == "history":
        memory.show()
        return ""

    if low == "help":
        console.print(Panel(HELP_TEXT, title="[bold green]Help[/bold green]"))
        return ""

    # ── Auto-route via orchestrator ───────────────────────────────────
    agent_type = classify_request(user_input)
    context = memory.recent_context()

    if agent_type == "summary":
        return run_summary(user_input, search_tool, context=context)
    elif agent_type == "mcq":
        return run_mcq(5, search_tool, topic=user_input, show_answers=True)
    else:
        return run_qa(user_input, search_tool, context=context)


# ── Main loop ────────────────────────────────────────────────────────────────

def main():
    args = _parse_args()

    # Determine files to ingest
    if args.files:
        files = [Path(f) for f in args.files]
    else:
        files = _default_sample_files()

    if not files:
        console.print(
            "[red]No files found. Provide files as arguments or "
            "run: python3 sample_data/generate_samples.py[/red]"
        )
        sys.exit(1)

    # Build RAG pipeline
    os.environ.setdefault("OLLAMA_MODEL", args.model)
    pipeline = RAGPipeline(model=args.model)

    console.print(Panel(
        f"[bold green]Financial Document Analyzer[/bold green]\n"
        f"Model: {args.model} | Files: {len(files)}",
        title="Starting",
    ))

    with console.status("[bold green]Ingesting documents..."):
        num_chunks = pipeline.ingest(files)
    console.print(f"[green]Ingested {num_chunks} chunks from {len(files)} files.[/green]\n")

    search_tool = DocumentSearchTool(pipeline=pipeline)
    memory = ConversationMemory()

    console.print(Panel(HELP_TEXT, title="[bold green]Financial Document Chat[/bold green]"))

    while True:
        try:
            user_input = console.input("\n[bold cyan]You:[/bold cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "/exit", "/quit"):
            console.print("[dim]Goodbye.[/dim]")
            break

        memory.add("user", user_input)

        with console.status("[bold green]Thinking..."):
            try:
                response = handle_command(user_input, pipeline, search_tool, memory)
            except Exception as e:
                response = f"Error: {e}"
                console.print(f"[red]{response}[/red]")
                continue

        if response:
            agent_tag = classify_request(user_input) if not user_input.lower().startswith(
                ("rag ", "qa ", "summary", "insights ", "mcq", "quiz", "docs", "history", "help")
            ) else ""
            memory.add("assistant", response, agent=agent_tag)
            console.print(f"\n[bold green]Assistant:[/bold green]")
            console.print(Markdown(response))


if __name__ == "__main__":
    main()
