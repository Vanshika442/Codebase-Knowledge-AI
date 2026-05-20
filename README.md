# ⚡ Codebase Knowledge AI

> Chat with any codebase. Ask questions, get cited answers from source files.

---

## 🚀 Demo VIDEO 
https://youtu.be/PuISpO8i0rE

---

## 📌 Overview
A LangChain-based developer tool that indexes entire repositories 
and answers natural language questions about code with 
**file-level citations** and **AST-aware retrieval**.

Solves the **onboarding problem** in large engineering teams by 
enabling developers to ask:
- "Where is the payment logic?"
- "How does auth flow work across files?"
- "Which functions handle data preprocessing?"

---

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

## ⚙️ Tech Stack
| Component | Technology |
|---|---|
| Framework | LangChain |
| LLM | Ollama (llama3.2 / qwen2.5-coder) |
| Embeddings | HuggingFace sentence-transformers |
| Vector DB | FAISS (local, CPU-friendly) |
| AST Parsing | Python ast module |
| UI | Streamlit |
| Repo Loading | GitPython |

---

## ✨ Key Features
1. **Language-aware chunking** using `RecursiveCharacterTextSplitter.from_language()`
2. **AST symbol extraction** - functions, classes, imports mapped per file
3. **MMR retrieval** - reduces duplicate/irrelevant chunks
4. **Source citations** - every answer includes `file:start_line-end_line`
5. **Line-range search** - ask "what is in README.md between lines 10-50"
6. **Repo stats** - total files, indexed files, binary files count
7. **Fully local** - no OpenAI API, no cost, runs on CPU

---

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



