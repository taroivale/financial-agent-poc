# Financial Document Analyzer — Multi-Agent Chatbot
A multi-agent system for deep financial document analysis combining:

* **RAG Pipeline** — LangChain + ChromaDB for retrieval-augmented generation
* **Agentic Workflows** — CrewAI agents for Q&A, summaries, and MCQ generation
* **Local LLM** — Ollama (default: `llama3.1:8b`), runs fully offline

## Architecture
```
                         User Query
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   Orchestrator (CrewAI)                      │
│            Routes requests via LLM classification           │
└──────────────┬──────────────┬──────────────────────────────┘
               │              │                │
       ┌───────▼──────┐ ┌────▼──────┐  ┌──────▼──────┐
       │   Q&A Agent  │ │  Summary  │  │  MCQ Agent  │
       │   (CrewAI)   │ │  Agent    │  │  (CrewAI)   │
       │              │ │ (CrewAI)  │  │              │
       └──────┬───────┘ └─────┬─────┘  └──────┬──────┘
              │               │                │
       ┌──────▼───────────────▼────────────────▼──────┐
       │          RAG Pipeline (LangChain)             │
       │   Retrieval from ChromaDB vector store        │
       └──────────────────┬───────────────────────────┘
                          │
       ┌──────────────────▼───────────────────────────┐
       │           Document Ingestion                  │
       │   PDF (pypdf) → chunks → embeddings           │
       │   CSV (pandas) → stats + rows → embeddings    │
       └───────────────────────────────────────────────┘
```
## Setup
1. Install [Ollama](https://ollama.com) and start it:

```bash
ollama serve
```
2. Install Python dependencies:

```bash
pip install -r requirements.txt
```
The default model (`llama3.1:8b`) is pulled automatically on first run if not already present.

## Usage
### Interactive chatbot (auto-routes to best agent)
```bash
python3 main.py                          # uses sample data
python3 main.py report.pdf finances.csv  # your own files
python3 main.py --model mistral          # override model
```
### Non-interactive demo
```bash
python3 demo.py
python3 demo.py --model mistral
```
## Chat Commands
| Command | Agent | Example |
|---------|-------|---------|
| Natural language | Auto-routed | `What was Q3 revenue?` |
| `rag <query>` | RAG Pipeline (direct) | `rag gross margin trend` |
| `qa <question>` | Q&A Agent | `qa What is the gross margin for June?` |
| `summary [topic]` | Summary Agent | `summary cash flow trends` |
| `insights <topic>` | Summary Agent | `insights regional sales performance` |
| `mcq [N] [topic]` | MCQ Agent (with answers) | `mcq 3 profitability` |
| `quiz [N] [topic]` | MCQ Agent (no answers) | `quiz 5` |
| `docs` | — | List loaded documents |
| `history` | — | Show conversation history |
| `help` | — | Show help |

## Components
### RAG Pipeline (`utils/rag_pipeline.py`)
Built with **LangChain** and **ChromaDB**:

* Loads PDFs and CSVs into LangChain `Document` objects
* Splits documents with `RecursiveCharacterTextSplitter` (1000-char chunks, 200-char overlap)
* Embeds chunks using Ollama embeddings and stores in ChromaDB vector store
* Provides `RetrievalQA` chain with a custom financial-analyst prompt
* Supports direct retrieval (`rag` command) and context retrieval for agents

### Q&A Agent (`agents/qa_agent.py`)
**CrewAI Agent** with role "Financial Q&A Analyst". Retrieves relevant chunks via RAG, then answers with citations and exact figures.

### Summary Agent (`agents/summary_agent.py`)
**CrewAI Agent** with role "Senior Financial Analyst". Produces structured executive summaries (Overview, Key Findings, Trends, Risks, Recommendations). Also supports focused `insights` queries with topic-specific RAG retrieval.

### MCQ Agent (`agents/mcq_agent.py`)
**CrewAI Agent** with role "Financial Education Specialist". Generates structured MCQs with 4 options (A–D), correct answers, explanations, difficulty ratings (Easy/Medium/Hard), and topic tags. Output validated via Pydantic models.

### Orchestrator (`agents/orchestrator.py`)
**CrewAI Agent** that classifies user requests into `qa`, `summary`, or `mcq` via JSON output, then dispatches to the appropriate specialist. Includes keyword-based fallback.

### Conversation Memory (`main.py`)
Maintains a rolling history of user/assistant turns (up to 50) with timestamps and agent tags. Viewable via the `history` command.

## Sample Data
Three synthetic financial datasets are included (regenerate with `python3 sample_data/generate_samples.py`):

* `quarterly_financials.csv` — Monthly P&L (Revenue, COGS, EBITDA, Net Income)
* `sales_by_region_product.csv` — Sales by region × product × month
* `budget_vs_actuals.csv` — Departmental budget vs actual spending

## Project Structure
```
financial_doc_analyzer/
├── main.py                     # Interactive chatbot (entry point)
├── demo.py                     # Non-interactive demo
├── requirements.txt            # Python dependencies
├── agents/
│   ├── orchestrator.py         # CrewAI request router
│   ├── qa_agent.py             # CrewAI Q&A agent
│   ├── summary_agent.py        # CrewAI summary/insights agent
│   └── mcq_agent.py            # CrewAI MCQ generator
├── utils/
│   ├── rag_pipeline.py         # LangChain RAG + ChromaDB pipeline
│   └── document_loader.py      # Legacy document loading utilities
└── sample_data/
    ├── generate_samples.py     # Sample data generator
    ├── quarterly_financials.csv
    ├── sales_by_region_product.csv
    └── budget_vs_actuals.csv
```
## Dependencies
| Package | Purpose |
|---------|---------|
| `langchain` | RAG pipeline, text splitting, retrieval chains |
| `langchain-community` | ChromaDB vector store integration |
| `langchain-ollama` | Ollama embeddings and chat model |
| `chromadb` | Vector storage for document embeddings |
| `crewai` | Agentic framework for multi-agent workflows |
| `crewai-tools` | Tool integrations for CrewAI agents |
| `ollama` | Local LLM inference backend |
| `pypdf` | PDF text extraction |
| `pandas` | CSV loading, statistics, and data preprocessing |
| `rich` | Terminal UI (panels, markdown, spinners) |
| `pydantic` | Structured output validation (MCQ agent) |

## Training Requirements Coverage
| Requirement | Implementation |
|---|---|
| **Python** | Data preprocessing with pandas (CSV stats, chunking), file I/O, Pydantic models |
| **Prompt Engineering** | Role-based system prompts, structured output instructions, few-shot JSON schema, chain-of-thought task descriptions |
| **RAG Pipeline (LangChain)** | `utils/rag_pipeline.py` — document ingestion, text splitting, ChromaDB embeddings, `RetrievalQA` chain |
| **Agents (CrewAI)** | All 4 agents (Q&A, Summary, MCQ, Orchestrator) built as CrewAI `Agent` + `Task` + `Crew` |
| **Presentation** | Demo script (`demo.py`) runs full pipeline end-to-end for live demonstration |
