"""
Capability 39: Documentation Generation
Extracts AST docstrings, formats Markdown API documentation,
and tracks documentation coverage for J.A.R.V.I.S.
"""

import ast
import pathlib
from typing import Dict, Any, List, Optional


class DocumentationGenerator:
    """Generates Markdown API references and computes documentation coverage."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = pathlib.Path(root_dir) if root_dir else pathlib.Path.cwd()

    def generate_module_docs(self, file_path: str) -> Dict[str, Any]:
        """
        Extracts docstrings and signatures from a single Python file to produce Markdown docs.
        """
        path = pathlib.Path(file_path)
        if not path.is_absolute():
            path = self.root_dir / path

        if not path.exists():
            return {"success": False, "error": f"File '{file_path}' not found."}

        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"), filename=str(path))
        except Exception as e:
            return {"success": False, "error": f"Failed to parse AST: {str(e)}"}

        mod_doc = ast.get_docstring(tree) or "No module docstring provided."
        rel_path = str(path.relative_to(self.root_dir))

        md_lines = [
            f"# Module `{path.stem}`",
            f"**File:** `{rel_path}`\n",
            f"## Overview",
            f"{mod_doc}\n",
            "---"
        ]

        classes_docs = []
        functions_docs = []
        total_items = 0
        documented_items = 0

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                total_items += 1
                c_doc = ast.get_docstring(node)
                if c_doc:
                    documented_items += 1

                c_bases = [self._format_node(b) for b in node.bases]
                bases_str = f"({', '.join(c_bases)})" if c_bases else ""
                md_lines.append(f"### Class `{node.name}{bases_str}`")
                md_lines.append(f"{c_doc or '_No class docstring._'}\n")

                methods = []
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        total_items += 1
                        m_doc = ast.get_docstring(child)
                        if m_doc:
                            documented_items += 1

                        m_args = self._format_args(child.args)
                        ret_ann = f" -> {self._format_node(child.returns)}" if child.returns else ""
                        md_lines.append(f"- **`{child.name}({m_args}){ret_ann}`**")
                        if m_doc:
                            md_lines.append(f"  > {m_doc.strip()}")
                        methods.append({"name": child.name, "doc": m_doc})

                md_lines.append("")
                classes_docs.append({"name": node.name, "doc": c_doc, "methods": methods})

            elif isinstance(node, ast.FunctionDef):
                total_items += 1
                f_doc = ast.get_docstring(node)
                if f_doc:
                    documented_items += 1

                f_args = self._format_args(node.args)
                ret_ann = f" -> {self._format_node(node.returns)}" if node.returns else ""
                md_lines.append(f"### Function `{node.name}({f_args}){ret_ann}`")
                md_lines.append(f"{f_doc or '_No function docstring._'}\n")
                functions_docs.append({"name": node.name, "doc": f_doc})

        coverage_pct = round((documented_items / total_items * 100), 1) if total_items > 0 else 100.0

        markdown = "\n".join(md_lines)
        return {
            "success": True,
            "module": path.stem,
            "path": rel_path,
            "markdown": markdown,
            "docstring_coverage_pct": coverage_pct,
            "total_symbols": total_items,
            "documented_symbols": documented_items,
            "classes": classes_docs,
            "functions": functions_docs
        }

    def audit_coverage(self, target_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Audits docstring coverage across all modules in directory.
        """
        base = pathlib.Path(target_dir) if target_dir else self.root_dir
        if not base.is_absolute():
            base = self.root_dir / base

        total_symbols = 0
        documented_symbols = 0
        module_reports = []

        for p in base.rglob("*.py"):
            if any(x in p.parts for x in [".git", "__pycache__", "node_modules", ".venv"]):
                continue

            doc_info = self.generate_module_docs(str(p))
            if doc_info.get("success"):
                tot = doc_info["total_symbols"]
                doc = doc_info["documented_symbols"]
                total_symbols += tot
                documented_symbols += doc
                module_reports.append({
                    "file": doc_info["path"],
                    "coverage_pct": doc_info["docstring_coverage_pct"],
                    "documented": doc,
                    "total": tot
                })

        overall_pct = round((documented_symbols / total_symbols * 100), 1) if total_symbols > 0 else 100.0

        return {
            "overall_coverage_pct": overall_pct,
            "total_symbols": total_symbols,
            "documented_symbols": documented_symbols,
            "modules": sorted(module_reports, key=lambda x: x["coverage_pct"])
        }

    def _format_args(self, args_node: ast.arguments) -> str:
        res = []
        for a in args_node.args:
            arg_str = a.arg
            if a.annotation:
                arg_str += f": {self._format_node(a.annotation)}"
            res.append(arg_str)
        return ", ".join(res)

    def _format_node(self, node: Optional[ast.AST]) -> str:
        if node is None:
            return ""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Attribute):
            return f"{self._format_node(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._format_node(node.value)}[{self._format_node(node.slice)}]"
        return "Any"
