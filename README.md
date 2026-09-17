# ⚡ Codebase Knowledge AI

> A production-deployed RAG (Retrieval-Augmented Generation) system that lets you chat with any GitHub repository — ask architecture questions, find functions, trace logic across files — and get answers with exact file + line-number citations.

🔗 **[Live Demo](https://codebase-knowledge-ai-xbfw3jsdezl34cgrdden2p.streamlit.app/)** **

---

## 🎯 Overview

Onboarding into a large, unfamiliar codebase is slow and frustrating. Traditional keyword search (grep/Ctrl+F) finds text, not meaning or relationships. **Codebase Knowledge AI** solves this by combining:

- **Semantic vector search** (understands *meaning*, not just keywords)
- **AST-based structural analysis** (understands *exact* code structure — functions, classes, imports)
- **LLM reasoning** (synthesizes both into a grounded, cited natural-language answer)

The result: ask *"Where is the payment logic?"* or *"How does auth flow work across these files?"* and get a precise, source-cited answer in seconds — not hours of manual searching.

---

## ✨ Key Features

- 🔍 **Hybrid Retrieval** — combines MMR-based semantic search with deterministic AST symbol lookup
- 📎 **File + Line-Level Citations** — every answer traces back to exact `file.py:start-end`
- 🧠 **AST Repo Map** — extracts every function, class, method, and import with line numbers using Python's `ast` module
- 🧩 **Language-Aware Chunking** — splits code at logical boundaries (functions/classes), not arbitrary character counts
- 📊 **Instant Stats Answers** — file/chunk counts answered directly without an LLM call
- 🎯 **Line-Range Search** — direct retrieval for queries like `engine.py 10-40`
- ☁️ **Cloud-Native** — stateless app, vectors persisted in managed cloud vector DB
- 🚫 **Hallucination-Resistant** — AST layer only surfaces symbols that actually exist in the code
- 🌐 **Multi-Repo Support** — index and query multiple repositories independently

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend / UI** | Streamlit | Interactive web app — indexing, Q&A, KPI dashboard |
| **Orchestration Framework** | LangChain | Document loading, chunking, retrieval pipeline glue |
| **LLM Inference** | Groq API (`gpt-oss-20b`) | Fast, free-tier cloud LLM for answer generation |
| **Vector Database** | Qdrant Cloud | Managed, persistent vector storage with MMR search |
| **Embeddings** | HuggingFace `all-MiniLM-L6-v2` | Converts code chunks into 384-dim semantic vectors |
| **AST Parsing** | Python `ast` module | Extracts exact function/class/import structure |
| **Code Loading & Parsing** | tree-sitter (via LangChain `LanguageParser`) | Multi-language-aware document loading |
| **Repo Management** | GitPython | Clone/pull GitHub repositories |
| **Deployment** | Streamlit Community Cloud | Free, public hosting |
| **Language** | Python 3.11 | Core implementation |

## 🏗️ Architecture & Workflow

The system works in two main phases: **Repository Indexing** and **Question Answering**.

```mermaid
flowchart TD

    %% =========================
    %% PHASE 1 - INDEXING
    %% =========================

    A["GitHub Repository / Local Path"] --> B["Clone / Load Repository"]
    B --> C["Load & Filter Code Files"]

    C --> D["Language-Aware Code Chunking"]
    C --> E["AST Parsing"]

    D --> F["Generate Embeddings"]
    E --> G["Repository Symbol Map"]

    F --> H[("Qdrant Cloud")]
    G --> I["repo_map.json"]
    D --> J["build_summary.json"]

    %% =========================
    %% PHASE 2 - QUERYING
    %% =========================

    K["User Question"] --> L{"Query Router"}

    L -->|"Stats Question"| J
    L -->|"Line-Range Request"| H
    L -->|"Semantic Question"| M["MMR Semantic Search"]
    L -->|"Symbol / Function Query"| N["AST Symbol Matching"]

    M --> H
    N --> I

    H --> O["Combine Retrieved Context"]
    I --> O

    O --> P["Groq LLM"]
    P --> Q["Grounded Answer + Citations"]

    J --> Q
    Q --> R["Streamlit UI"]

    %% =========================
    %% STYLING
    %% =========================

    classDef input fill:#e8f4fd,stroke:#3498db,stroke-width:2px
    classDef process fill:#f4f4f4,stroke:#555,stroke-width:1.5px
    classDef database fill:#fff3cd,stroke:#d39e00,stroke-width:2px
    classDef output fill:#e8f8f0,stroke:#27ae60,stroke-width:2px

    class A,K input
    class B,C,D,E,F,G,L,M,N,O,P process
    class H,I,J database
    class Q,R output

### 🔹 Phase 1 — Repository Indexing

This phase runs when a repository is indexed.

1. **Clone / Load Repository** — GitPython loads the GitHub repository or local project.
2. **Load & Filter Files** — Relevant source-code files are identified.
3. **Language-Aware Chunking** — Code is split into meaningful chunks while preserving code structure.
4. **AST Parsing** — Python's `ast` module extracts functions, classes, methods, imports, and line numbers.
5. **Generate Embeddings** — HuggingFace `all-MiniLM-L6-v2` converts code chunks into semantic vectors.
6. **Store Vectors** — Embeddings and metadata are stored in a dedicated Qdrant Cloud collection.
7. **Build Repository Metadata** — `repo_map.json` stores symbols and their exact locations, while `build_summary.json` stores indexing statistics.

### 🔹 Phase 2 — Question Answering

This phase runs whenever the user asks a question.

1. **User Question** — The user submits a question through the Streamlit interface.
2. **Query Router** — Determines what type of question was asked.
3. **Stats Questions** — Retrieved directly from `build_summary.json` without using the LLM.
4. **Line-Range Requests** — Relevant code is directly retrieved from Qdrant.
5. **Semantic Questions** — MMR search retrieves diverse and relevant code chunks.
6. **AST Symbol Matching** — Exact functions, classes, or imports are identified from the repository map.
7. **Context Combination** — Semantic results and AST information are combined.
8. **Groq LLM** — The retrieved context is passed to the LLM to generate a grounded response.
9. **Streamlit UI** — Displays the answer, citations, AST hints, and retrieved context.
