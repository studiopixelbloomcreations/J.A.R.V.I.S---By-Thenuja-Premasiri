"""
Capability 32: Repository Understanding
Provides deep codebase indexing, AST symbol extraction, file-tree mapping,
and structural call graph insights for J.A.R.V.I.S.
"""

import ast
import os
import pathlib
from typing import Dict, Any, List, Optional, Set


class RepoAnalyzer:
    """Understands and maps codebase structure using Python AST and file analysis."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = pathlib.Path(root_dir) if root_dir else pathlib.Path.cwd()
        self.ignore_patterns = {
            ".git", "__pycache__", "node_modules", ".venv", "venv", ".idea",
            ".vscode", "dist", "build", ".pytest_cache", ".coverage"
        }

    def is_ignored(self, path: pathlib.Path) -> bool:
        """Checks if a path should be excluded from analysis."""
        return any(part in self.ignore_patterns for part in path.parts)

    def scan_repository(self, target_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Scans repository directory and returns high-level structural metrics.
        """
        base = pathlib.Path(target_dir) if target_dir else self.root_dir
        if not base.is_absolute():
            base = self.root_dir / base

        total_files = 0
        total_lines = 0
        ext_counts: Dict[str, int] = {}
        file_tree: List[Dict[str, Any]] = []

        for root, dirs, files in os.walk(base):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns]
            r_path = pathlib.Path(root)
            if self.is_ignored(r_path):
                continue

            for file in files:
                f_path = r_path / file
                if self.is_ignored(f_path):
                    continue

                total_files += 1
                ext = f_path.suffix.lower() or "no_ext"
                ext_counts[ext] = ext_counts.get(ext, 0) + 1

                file_loc = 0
                if f_path.is_file():
                    try:
                        with open(f_path, "r", encoding="utf-8", errors="ignore") as f:
                            lines = f.readlines()
                            file_loc = len(lines)
                            total_lines += file_loc
                    except Exception:
                        pass

                rel_path = str(f_path.relative_to(self.root_dir))
                file_tree.append({
                    "path": rel_path,
                    "filename": file,
                    "extension": ext,
                    "lines": file_loc,
                    "size_bytes": f_path.stat().st_size
                })

        return {
            "root_dir": str(base),
            "total_files": total_files,
            "total_lines": total_lines,
            "extension_distribution": ext_counts,
            "file_count_by_ext": sorted(ext_counts.items(), key=lambda x: x[1], reverse=True),
            "files": file_tree
        }

    def index_symbols(self, target_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Parses all Python files via AST and returns index of classes, functions, and methods.
        """
        base = pathlib.Path(target_dir) if target_dir else self.root_dir
        if not base.is_absolute():
            base = self.root_dir / base

        classes: List[Dict[str, Any]] = []
        functions: List[Dict[str, Any]] = []
        module_count = 0

        for f_path in base.rglob("*.py"):
            if self.is_ignored(f_path):
                continue

            module_count += 1
            rel_file = str(f_path.relative_to(self.root_dir))
            try:
                content = f_path.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content, filename=str(f_path))
            except Exception:
                continue

            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    methods = []
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            args = [arg.arg for arg in child.args.args]
                            methods.append({
                                "name": child.name,
                                "line": child.lineno,
                                "args": args,
                                "docstring": ast.get_docstring(child)
                            })
                    classes.append({
                        "name": node.name,
                        "file": rel_file,
                        "line": node.lineno,
                        "docstring": ast.get_docstring(node),
                        "methods": methods,
                        "base_classes": [self._get_name(b) for b in node.bases]
                    })
                elif isinstance(node, ast.FunctionDef):
                    args = [arg.arg for arg in node.args.args]
                    functions.append({
                        "name": node.name,
                        "file": rel_file,
                        "line": node.lineno,
                        "args": args,
                        "docstring": ast.get_docstring(node)
                    })

        return {
            "modules_indexed": module_count,
            "total_classes": len(classes),
            "total_functions": len(functions),
            "classes": classes,
            "functions": functions
        }

    def find_symbol(self, symbol_name: str, target_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Finds occurrences and definitions of a symbol across codebase.
        """
        symbols = self.index_symbols(target_dir)
        results = []
        target = symbol_name.lower()

        for c in symbols["classes"]:
            if target in c["name"].lower():
                results.append({"type": "class", "symbol": c})
            for m in c["methods"]:
                if target in m["name"].lower():
                    results.append({"type": "method", "class": c["name"], "file": c["file"], "method": m})

        for f in symbols["functions"]:
            if target in f["name"].lower():
                results.append({"type": "function", "symbol": f})

        return results

    def _get_name(self, node: ast.AST) -> str:
        """Helper to get string representation of AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return "Unknown"
