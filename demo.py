#!/usr/bin/env python3
"""
Non-interactive demo — runs the full pipeline end-to-end.

Usage:
    python3 demo.py
    python3 demo.py --model mistral
"""
import argparse
import os
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from utils.rag_pipeline import RAGPipeline
from agents.tools import DocumentSearchTool
from agents.qa_agent import run_qa
from agents.summary_agent import run_summary
from agents.mcq_agent import run_mcq

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Financial Analyzer Demo")
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "llama3.1:8b"))
    args = parser.parse_args()

    os.environ.setdefault("OLLAMA_MODEL", args.model)

    # Find sample data
    sample_dir = Path(__file__).parent / "sample_data"
    files = sorted(sample_dir.glob("*.csv")) + sorted(sample_dir.glob("*.pdf"))
    if not files:
        console.print("[red]No sample data found. Run: python3 sample_data/generate_samples.py[/red]")
        return

    console.print(Panel(
        f"[bold green]Financial Document Analyzer — Demo[/bold green]\n"
        f"Model: {args.model} | Files: {len(files)}",
    ))

    # 1. Ingest
    pipeline = RAGPipeline(model=args.model)
    with console.status("[bold green]Ingesting documents..."):
        num_chunks = pipeline.ingest(files)
    console.print(f"[green]Ingested {num_chunks} chunks.[/green]\n")

    search_tool = DocumentSearchTool(pipeline=pipeline)

    # 2. Direct RAG query
    console.print(Panel("[bold]Step 1: Direct RAG Query[/bold]"))
    question = "What are the main revenue figures and growth trends?"
    console.print(f"[cyan]Query:[/cyan] {question}\n")
    with console.status("Querying RAG pipeline..."):
        answer = pipeline.query(question)
    console.print(Markdown(answer))

    # 3. Q&A Agent
    console.print(Panel("[bold]Step 2: Q&A Agent[/bold]"))
    question = "What is the gross margin trend over the past 5 years?"
    console.print(f"[cyan]Question:[/cyan] {question}\n")
    with console.status("Running Q&A agent..."):
        answer = run_qa(question, search_tool)
    console.print(Markdown(answer))

    # 4. Summary Agent
    console.print(Panel("[bold]Step 3: Summary Agent[/bold]"))
    console.print("[cyan]Topic:[/cyan] overall financial performance\n")
    with console.status("Running summary agent..."):
        summary = run_summary("overall financial performance", search_tool)
    console.print(Markdown(summary))

    # 5. MCQ Agent
    console.print(Panel("[bold]Step 4: MCQ Agent (3 questions)[/bold]"))
    with console.status("Generating MCQs..."):
        mcqs = run_mcq(3, search_tool, topic="profitability")
    console.print(mcqs)

    console.print("\n[bold green]Demo complete.[/bold green]")


if __name__ == "__main__":
    main()
