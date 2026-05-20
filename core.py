import os
import re
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv
from ollama import Client
from sentence_transformers import SentenceTransformer

load_dotenv()

DATA_DIR = Path("data")
REPOS_DIR = DATA_DIR / "repos"
FAISS_DIR = DATA_DIR / "faiss"

REPOS_DIR.mkdir(parents=True, exist_ok=True)
FAISS_DIR.mkdir(parents=True, exist_ok=True)

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHUNK_LINES = int(os.getenv("CHUNK_LINES", "80"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "12"))
TOP_K = int(os.getenv("TOP_K", "5"))
MAX_FILES = int(os.getenv("MAX_FILES", "1200"))

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "coverage",
}

ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs",
    ".cpp", ".c", ".h", ".hpp", ".cs", ".rb", ".php", ".swift",
    ".kt", ".sql", ".md", ".json", ".yaml", ".yml", ".toml"
}

_embedding_model = None
_ollama_client = None


def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBED_MODEL)
    return _embedding_model


def get_ollama_client() -> Client:
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = Client()
    return _ollama_client


def is_git_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://") or value.startswith("git@")


def slugify_repo_id(value: str) -> str:
    value = value.strip().rstrip("/")
    name = value.split("/")[-1]
    name = name.replace(".git", "")
    name = re.sub(r"[^a-zA-Z0-9_-]+", "-", name).strip("-").lower()
    return name or "repo"


def collect_code_files(repo_path: Path, max_files: int = MAX_FILES) -> List[Path]:
    collected: List[Path] = []
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        root_path = Path(root)
        for filename in files:
            file_path = root_path / filename
            if file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                collected.append(file_path)
                if len(collected) >= max_files:
                    return collected
    return collected


def read_text_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="ignore")


def chunk_code(text: str, chunk_lines: int = CHUNK_LINES, overlap: int = CHUNK_OVERLAP) -> List[Tuple[int, int, str]]:
    lines = text.splitlines()
    if not lines:
        return []

    chunks: List[Tuple[int, int, str]] = []
    start = 0
    total = len(lines)

    while start < total:
        end = min(start + chunk_lines, total)
        chunk_text = "\n".join(lines[start:end]).strip()
        if chunk_text:
            chunks.append((start + 1, end, chunk_text))
        if end == total:
            break
        start = max(end - overlap, start + 1)

    return chunks