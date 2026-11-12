"""
Capability 36: Code Review
Performs AST-driven static analysis, code smell detection,
security checks, and quality scoring for J.A.R.V.I.S.
"""

import ast
import re
import pathlib
from typing import Dict, Any, List, Optional


class CodeReviewer(ast.NodeVisitor):
    """Static analysis inspector identifying antipatterns and security flaws."""

    def __init__(self):
        super().__init__()
        self.issues: List[Dict[str, Any]] = []
        self.complexity_map: Dict[str, int] = {}
        self.current_function: Optional[str] = None

    def review_code(self, code_str: str, filename: str = "snippet.py") -> Dict[str, Any]:
        """
        Runs comprehensive code review on a source code string.
        """
        self.issues = []
        self.complexity_map = {}
        self.current_function = None

        try:
            tree = ast.parse(code_str, filename=filename)
        except SyntaxError as e:
            return {
                "score": 0,
                "passed": False,
                "syntax_error": f"Line {e.lineno}: {e.msg}",
                "issues": [{
                    "severity": "CRITICAL",
                    "rule": "SYNTAX_ERROR",
                    "line": e.lineno or 1,
                    "message": f"Code contains invalid Python syntax: {e.msg}",
                    "suggestion": "Fix syntax error before running static review."
                }],
                "summary": {"critical": 1, "high": 0, "medium": 0, "low": 0}
            }

        # 1. AST Checks
        self.visit(tree)

        # 2. Regex checks on source text
        self._check_secrets_and_patterns(code_str)

        # 3. Compute overall score
        score = 100
        critical_count = sum(1 for i in self.issues if i["severity"] == "CRITICAL")
        high_count = sum(1 for i in self.issues if i["severity"] == "HIGH")
        med_count = sum(1 for i in self.issues if i["severity"] == "MEDIUM")
        low_count = sum(1 for i in self.issues if i["severity"] == "LOW")

        score -= (critical_count * 30 + high_count * 15 + med_count * 5 + low_count * 2)
        score = max(0, min(100, score))

        return {
            "score": score,
            "passed": score >= 70 and high_count == 0 and critical_count == 0,
            "filename": filename,
            "total_issues": len(self.issues),
            "summary": {
                "critical": critical_count,
                "high": high_count,
                "medium": med_count,
                "low": low_count
            },
            "issues": sorted(self.issues, key=lambda x: (
                {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(x["severity"], 4),
                x.get("line", 0)
            ))
        }

    def review_file(self, file_path: str) -> Dict[str, Any]:
        """Reviews a python file from disk."""
        path = pathlib.Path(file_path)
        if not path.exists():
            return {"score": 0, "passed": False, "error": f"File '{file_path}' not found."}
        content = path.read_text(encoding="utf-8", errors="ignore")
        return self.review_code(content, filename=path.name)

    # ── AST Visitors ──────────────────────────────────────────────────

    def visit_FunctionDef(self, node: ast.FunctionDef):
        prev_func = self.current_function
        self.current_function = node.name

        # Check missing docstring for non-private functions
        if not node.name.startswith("_") and not ast.get_docstring(node):
            self.issues.append({
                "severity": "LOW",
                "rule": "MISSING_DOCSTRING",
                "line": node.lineno,
                "message": f"Public function '{node.name}' has no docstring.",
                "suggestion": f"Add descriptive docstring explaining purpose, parameters, and return value."
            })

        # Check too many parameters (> 6)
        param_count = len(node.args.args)
        if param_count > 6:
            self.issues.append({
                "severity": "MEDIUM",
                "rule": "TOO_MANY_PARAMETERS",
                "line": node.lineno,
                "message": f"Function '{node.name}' accepts {param_count} parameters (limit recommended is 6).",
                "suggestion": "Refactor parameters into a configuration dataclass or dictionary."
            })

        # Check mutable default arguments (e.g. def fn(a=[]):)
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.issues.append({
                    "severity": "HIGH",
                    "rule": "MUTABLE_DEFAULT_ARG",
                    "line": default.lineno,
                    "message": f"Function '{node.name}' defines a mutable default argument.",
                    "suggestion": "Use None as the default argument and initialize inside function body (e.g., if arg is None: arg = [])."
                })

        # Check function length
        lines = (node.end_lineno - node.lineno) if hasattr(node, "end_lineno") and node.end_lineno else len(node.body)
        if lines > 60:
            self.issues.append({
                "severity": "MEDIUM",
                "rule": "LONG_FUNCTION",
                "line": node.lineno,
                "message": f"Function '{node.name}' is {lines} lines long (recommend < 60).",
                "suggestion": "Decompose into smaller helper functions."
            })

        self.generic_visit(node)
        self.current_function = prev_func

    def visit_Try(self, node: ast.Try):
        # Check for bare 'except:'
        for handler in node.handlers:
            if handler.type is None:
                self.issues.append({
                    "severity": "HIGH",
                    "rule": "BARE_EXCEPT",
                    "line": handler.lineno,
                    "message": "Bare 'except:' catches BaseException (including KeyboardInterrupt and SystemExit).",
                    "suggestion": "Specify concrete exceptions or use 'except Exception:'."
                })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        # Check wildcard imports (from foo import *)
        for alias in node.names:
            if alias.name == "*":
                self.issues.append({
                    "severity": "MEDIUM",
                    "rule": "WILDCARD_IMPORT",
                    "line": node.lineno,
                    "message": f"Wildcard import 'from {node.module or ''} import *' pollutes namespace.",
                    "suggestion": "Import only required explicit symbols."
                })
        self.generic_visit(node)

    # ── Regex and Text Pattern Checks ──────────────────────────────────

    def _check_secrets_and_patterns(self, code_str: str):
        secret_patterns = [
            (r'(?i)(api[_-]?key|secret|password|access[_-]?token)\s*=\s*["\'][A-Za-z0-9_\-\.]{8,}["\']', "HARDCODED_SECRET", "HIGH", "Hardcoded secret or credential detected in source code."),
            (r'print\s*\([^)]*\)', "LEFTOVER_PRINT", "LOW", "Print statement found; consider using structured logging."),
            (r'time\.sleep\(\s*(?:[1-9]\d{1,}|[5-9])\s*\)', "LONG_BLOCKING_SLEEP", "MEDIUM", "Long synchronous blocking sleep found.")
        ]

        lines = code_str.splitlines()
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue

            for pattern, rule, severity, msg in secret_patterns:
                # Don't flag pattern definitions in reviewer itself!
                if 'secret_patterns' in stripped or 'r\'(?i)' in stripped:
                    continue
                if re.search(pattern, line):
                    self.issues.append({
                        "severity": severity,
                        "rule": rule,
                        "line": idx,
                        "message": msg,
                        "suggestion": f"Check line {idx}: {stripped[:60]}"
                    })
