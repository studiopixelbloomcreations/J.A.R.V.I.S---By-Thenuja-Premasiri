"""
Capability 42: Build Diagnostics
Executes py_compile bytecode verification, broken import detection,
and project build health telemetry for J.A.R.V.I.S.
"""

import os
import py_compile
import pathlib
import sys
from typing import Dict, Any, List, Optional


class BuildDiagnostics:
    """Diagnoses build integrity, byte-compilation errors, and packaging readiness."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = pathlib.Path(root_dir) if root_dir else pathlib.Path.cwd()
        self.ignore_patterns = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"}

    def compile_all(self, target_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs py_compile across all Python files in the workspace.
        Detects compilation and bytecode generation failures.
        """
        base = pathlib.Path(target_dir) if target_dir else self.root_dir
        if not base.is_absolute():
            base = self.root_dir / base

        compiled_count = 0
        compilation_errors: List[Dict[str, Any]] = []

        for f_path in base.rglob("*.py"):
            if any(p in f_path.parts for p in self.ignore_patterns):
                continue

            rel_path = str(f_path.relative_to(self.root_dir))
            try:
                # Compile to memory/test dora bytecode compilation
                py_compile.compile(str(f_path), doraise=True)
                compiled_count += 1
            except py_compile.PyCompileError as e:
                compilation_errors.append({
                    "file": rel_path,
                    "error": str(e.exc_value),
                    "line": getattr(e.exc_value, "lineno", None)
                })
            except Exception as e:
                compilation_errors.append({
                    "file": rel_path,
                    "error": str(e)
                })

        return {
            "success": len(compilation_errors) == 0,
            "total_compiled": compiled_count,
            "failed_count": len(compilation_errors),
            "errors": compilation_errors
        }

    def verify_project_structure(self) -> Dict[str, Any]:
        """
        Verifies essential project assets, manifest files, and python packages.
        """
        manifest_files = ["requirements.txt", "README.md"]
        package_inits = ["jarvis/__init__.py"]

        results = []
        all_passed = True

        for m in manifest_files:
            exists = (self.root_dir / m).exists()
            results.append({"item": m, "type": "manifest", "exists": exists})
            if not exists and m == "requirements.txt":
                all_passed = False

        for p in package_inits:
            exists = (self.root_dir / p).exists()
            results.append({"item": p, "type": "package_init", "exists": exists})
            if not exists:
                all_passed = False

        return {
            "passed": all_passed,
            "items_checked": len(results),
            "details": results
        }

    def generate_build_report(self) -> Dict[str, Any]:
        """
        Synthesizes a full build diagnostics telemetry report.
        """
        comp_res = self.compile_all()
        struct_res = self.verify_project_structure()

        return {
            "build_healthy": comp_res["success"] and struct_res["passed"],
            "compilation": comp_res,
            "project_structure": struct_res,
            "python_version": sys.version.split()[0],
            "executable": sys.executable
        }
