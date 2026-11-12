"""
Capability 38: Dependency Analysis
Inspects requirements specifications, installed packages, missing dependencies,
and version constraints for J.A.R.V.I.S.
"""

import ast
import os
import re
import pathlib
import sys
from typing import Dict, Any, List, Set, Optional

try:
    import importlib.metadata as importlib_metadata
except ImportError:
    import importlib_metadata  # type: ignore


class DependencyAnalyzer:
    """Audits project requirements against runtime environment and codebase imports."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = pathlib.Path(root_dir) if root_dir else pathlib.Path.cwd()
        self.standard_libs = set(sys.builtin_module_names) | {
            "os", "sys", "re", "json", "time", "shutil", "hashlib", "zipfile",
            "pathlib", "platform", "subprocess", "urllib", "ctypes", "unittest",
            "socket", "threading", "tempfile", "ast", "difflib", "traceback",
            "math", "random", "datetime", "typing", "collections", "itertools",
            "functools", "logging", "asyncio", "sqlite3", "csv", "xml", "http",
            "inspect", "importlib", "uuid", "copy", "io", "contextlib"
        }

    def parse_requirements(self, req_path: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Parses a requirements.txt file into package names and version specifiers.
        """
        path = pathlib.Path(req_path) if req_path else self.root_dir / "requirements.txt"
        if not path.is_absolute():
            path = self.root_dir / path

        if not path.exists():
            return []

        specs = []
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue

            # Split package and version operators (==, >=, <=, ~=, !=)
            m = re.match(r"^([a-zA-Z0-9_\-\.]+)(.*)$", line)
            if m:
                pkg_name = m.group(1).strip()
                version_spec = m.group(2).strip()
                specs.append({
                    "package": pkg_name,
                    "specifier": version_spec,
                    "raw": line
                })

        return specs

    def get_installed_packages(self) -> Dict[str, str]:
        """
        Returns dictionary of all installed packages in active Python environment.
        """
        installed = {}
        try:
            for dist in importlib_metadata.distributions():
                name = dist.metadata["Name"] if "Name" in dist.metadata else dist.name
                if name:
                    installed[name.lower().replace("_", "-")] = dist.version
        except Exception:
            pass
        return installed

    def scan_imported_modules(self, target_dir: Optional[str] = None) -> Set[str]:
        """
        Collects all top-level imported module names across repository.
        """
        base = pathlib.Path(target_dir) if target_dir else self.root_dir
        if not base.is_absolute():
            base = self.root_dir / base

        imported = set()
        for f in base.rglob("*.py"):
            if any(p in f.parts for p in [".git", "__pycache__", "node_modules", ".venv", "venv"]):
                continue
            try:
                tree = ast.parse(f.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        top = a.name.split(".")[0]
                        imported.add(top)
                elif isinstance(node, ast.ImportFrom):
                    if node.level == 0 and node.module:
                        top = node.module.split(".")[0]
                        imported.add(top)

        return imported

    def audit_dependencies(self, req_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Audits project requirements against runtime environment and codebase imports.
        """
        reqs = self.parse_requirements(req_path)
        installed = self.get_installed_packages()
        imported = self.scan_imported_modules()

        # Check missing declared dependencies
        missing_installed = []
        satisfied_declared = []

        for r in reqs:
            norm_pkg = r["package"].lower().replace("_", "-")
            if norm_pkg in installed:
                satisfied_declared.append({
                    "package": r["package"],
                    "specifier": r["specifier"],
                    "installed_version": installed[norm_pkg]
                })
            else:
                missing_installed.append(r)

        # External imports that are not in stdlib or local project
        third_party_imported = []
        for imp in sorted(imported):
            if imp in self.standard_libs:
                continue
            # Check if it's a local directory in root
            if (self.root_dir / imp).is_dir() or (self.root_dir / f"{imp}.py").is_file():
                continue
            third_party_imported.append(imp)

        return {
            "total_declared": len(reqs),
            "declared_requirements": reqs,
            "installed_count": len(installed),
            "satisfied_declared": satisfied_declared,
            "missing_installed": missing_installed,
            "third_party_imports": third_party_imported,
            "all_declared_satisfied": len(missing_installed) == 0
        }
