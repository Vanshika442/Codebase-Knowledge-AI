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

## 🏗️ Architecture / Workflow

```mermaid
flowchart TD
    A[GitHub URL or Local Path] --> B[Clone / Load Repository]
    B --> C[Language-Aware Chunking<br/>RecursiveCharacterTextSplitter]
    B --> D[AST Parsing<br/>Python ast module]
    C --> E[Generate Embeddings<br/>HuggingFace all-MiniLM-L6-v2]
    D --> F[repo_map.json<br/>functions, classes, imports + line numbers]
    E --> G[(Qdrant Cloud<br/>Vector Database)]
    F --> H[build_summary.json<br/>index stats]

    I[User Question] --> J{Query Router}
    J -->|Stats question| H
    J -->|Line-range pattern| G
    J -->|Semantic question| K[MMR Search on Qdrant]
    K --> G
    J -->|Semantic question| L[AST Symbol Matching]
    L --> F
    K --> M[Combine Context + AST Hints]
    L --> M
    M --> N[Groq LLM<br/>llama / gpt-oss model]
    N --> O[Answer + Citations + AST Hints]
    O --> P[Streamlit UI]

## 🧠 Architecture
Codebase / GitHub URL
↓
Repository Loader (GenericLoader + LanguageParser)
↓
File Splitter + AST Parser (RecursiveCharacterTextSplitter + ast module)
↓
Embedding Generator (HuggingFace: all-MiniLM-L6-v2)
↓
Vector DB Index (FAISS)
↑ ↑
User Question Context Retriever (MMR Search)
↓
Code-Aware LLM Response (Ollama: llama3.2 / qwen2.5-coder)
↓
Answer with File References (path:start_line-end_line)


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

## 🏃 How To Run

### 1. Install Ollama and pull model
```bash
ollama pull llama3.2:latest

### 2.Clone this repo
git clone https://github.com/yourusername/codebase-knowledge-ai.git
cd codebase-knowledge-ai

3. Install dependencies
pip install -r requirements.txt

4. Setup environment
cp .env.example .env

5. Run app
streamlit run app.py
---
##Future Enhancements
PR Reviewer using repo knowledge base
VS Code extension integration
Multi-repo search across microservices
Incremental indexing on git push webhook
GPU support for faster inference



