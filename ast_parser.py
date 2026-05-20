import ast
import json
from pathlib import Path
from typing import Dict, List, Any


def _safe_read(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="ignore")


def _parse_python_file(file_path: Path, repo_root: Path) -> Dict[str, Any]:
    text = _safe_read(file_path)
    rel = str(file_path.relative_to(repo_root))

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {
            "file": rel,
            "language": "python",
            "imports": [],
            "functions": [],
            "classes": [],
        }

    imports: List[str] = []
    functions: List[Dict[str, Any]] = []
    classes: List[Dict[str, Any]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            imports.append(mod)
        elif isinstance(node, ast.FunctionDef):
            functions.append(
                {
                    "name": node.name,
                    "start_line": getattr(node, "lineno", None),
                    "end_line": getattr(node, "end_lineno", None),
                }
            )
        elif isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append(
                        {
                            "name": item.name,
                            "start_line": getattr(item, "lineno", None),
                            "end_line": getattr(item, "end_lineno", None),
                        }
                    )
            classes.append(
                {
                    "name": node.name,
                    "start_line": getattr(node, "lineno", None),
                    "end_line": getattr(node, "end_lineno", None),
                    "methods": methods,
                }
            )

    return {
        "file": rel,
        "language": "python",
        "imports": sorted(list(set([x for x in imports if x]))),
        "functions": functions,
        "classes": classes,
    }


def build_repo_map(repo_path: Path, output_path: Path) -> Dict[str, Any]:
    python_files = list(repo_path.rglob("*.py"))
    ignored = {".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__"}

    entries = []
    for f in python_files:
        if any(part in ignored for part in f.parts):
            continue
        entries.append(_parse_python_file(f, repo_path))

    repo_map = {
        "repo": repo_path.name,
        "files": entries,
        "total_python_files": len(entries),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(repo_map, indent=2), encoding="utf-8")
    return repo_map