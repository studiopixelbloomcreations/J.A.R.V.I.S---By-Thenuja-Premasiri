"""
Capability 37: Architecture Analysis
Analyzes module dependency graphs, circular import cycles,
coupling/instability metrics, and layer boundaries for J.A.R.V.I.S.
"""

import ast
import os
import pathlib
from typing import Dict, Any, List, Set, Tuple, Optional


class ArchitectureAnalyzer:
    """Builds dependency graphs and verifies software architectural constraints."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = pathlib.Path(root_dir) if root_dir else pathlib.Path.cwd()
        self.ignore_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"}

    def analyze_dependencies(self, target_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Parses all Python files and maps internal import dependencies.
        """
        base = pathlib.Path(target_dir) if target_dir else self.root_dir
        if not base.is_absolute():
            base = self.root_dir / base

        graph: Dict[str, Set[str]] = {}
        all_modules: Set[str] = set()

        for f_path in base.rglob("*.py"):
            if any(p in f_path.parts for p in self.ignore_dirs):
                continue

            rel_mod = str(f_path.relative_to(self.root_dir)).replace("\\", "/").replace(".py", "")
            if rel_mod.endswith("/__init__"):
                rel_mod = rel_mod[:-9]
            
            all_modules.add(rel_mod)
            if rel_mod not in graph:
                graph[rel_mod] = set()

            try:
                tree = ast.parse(f_path.read_text(encoding="utf-8", errors="ignore"), filename=str(f_path))
            except Exception:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        graph[rel_mod].add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ""
                    # Handle relative imports
                    if node.level > 0:
                        prefix_parts = rel_mod.split("/")[:-node.level]
                        if mod:
                            resolved = "/".join(prefix_parts + [mod])
                        else:
                            resolved = "/".join(prefix_parts)
                        graph[rel_mod].add(resolved)
                    else:
                        graph[rel_mod].add(mod)

        # Convert sets to sorted lists for clean JSON serialization
        serialized_graph = {k: sorted(list(v)) for k, v in graph.items()}

        # Filter internal dependencies
        internal_graph = {}
        for mod, deps in graph.items():
            internal_deps = set()
            for d in deps:
                d_normalized = d.replace(".", "/")
                for known in all_modules:
                    if d_normalized == known or d_normalized.startswith(known + "/"):
                        internal_deps.add(known)
            internal_graph[mod] = sorted(list(internal_deps))

        return {
            "root_dir": str(base),
            "total_modules": len(all_modules),
            "modules": sorted(list(all_modules)),
            "full_dependencies": serialized_graph,
            "internal_dependencies": internal_graph
        }

    def detect_circular_imports(self, target_dir: Optional[str] = None) -> List[List[str]]:
        """
        Detects circular dependency cycles using depth-first search cycle detection.
        """
        deps_data = self.analyze_dependencies(target_dir)
        graph = deps_data["internal_dependencies"]

        cycles: List[List[str]] = []
        visited: Set[str] = set()
        rec_stack: List[str] = []

        def dfs(node: str):
            visited.add(node)
            rec_stack.append(node)

            for neighbor in graph.get(node, []):
                if neighbor == node:
                    continue  # Self-loop ignored
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found cycle
                    idx = rec_stack.index(neighbor)
                    cycle = rec_stack[idx:] + [neighbor]
                    # Check if cycle already recorded in some rotation
                    canon = self._canonical_cycle(cycle)
                    if canon not in [self._canonical_cycle(c) for c in cycles]:
                        cycles.append(cycle)

            rec_stack.pop()

        for mod in graph:
            if mod not in visited:
                dfs(mod)

        return cycles

    def _canonical_cycle(self, cycle: List[str]) -> Tuple[str, ...]:
        """Returns normalized rotation of a cycle."""
        nodes = cycle[:-1]
        if not nodes:
            return tuple()
        rotations = [nodes[i:] + nodes[:i] for i in range(len(nodes))]
        return tuple(min(rotations))

    def calculate_metrics(self, target_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculates Robert C. Martin coupling metrics:
        - Afferent Coupling (Ca): Number of incoming dependencies
        - Efferent Coupling (Ce): Number of outgoing dependencies
        - Instability (I): Ce / (Ca + Ce) (0 = completely stable, 1 = completely unstable)
        """
        deps_data = self.analyze_dependencies(target_dir)
        graph = deps_data["internal_dependencies"]

        ca: Dict[str, int] = {m: 0 for m in graph}
        ce: Dict[str, int] = {m: len(deps) for m, deps in graph.items()}

        for src, targets in graph.items():
            for t in targets:
                if t in ca:
                    ca[t] += 1

        metrics = {}
        for m in graph:
            outgoing = ce[m]
            incoming = ca[m]
            total = incoming + outgoing
            instability = round(outgoing / total, 3) if total > 0 else 0.0
            metrics[m] = {
                "afferent_coupling_ca": incoming,
                "efferent_coupling_ce": outgoing,
                "instability": instability
            }

        return {
            "total_modules": len(metrics),
            "coupling_metrics": metrics
        }

    def check_layer_violations(
        self,
        forbidden_rules: Optional[List[Dict[str, str]]] = None,
        target_dir: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Validates architectural layer boundaries.
        Example rule: {"from_layer": "jarvis/core", "cannot_import": "jarvis/viewer"}
        """
        if forbidden_rules is None:
            forbidden_rules = [
                {"from_layer": "jarvis/core", "cannot_import": "viewer"},
                {"from_layer": "jarvis/core", "cannot_import": "jarvis/viewer"},
            ]

        deps_data = self.analyze_dependencies(target_dir)
        graph = deps_data["full_dependencies"]
        violations = []

        for mod, targets in graph.items():
            for rule in forbidden_rules:
                from_p = rule["from_layer"]
                bad_p = rule["cannot_import"]
                if from_p in mod:
                    for t in targets:
                        if bad_p in t:
                            violations.append({
                                "module": mod,
                                "illegal_import": t,
                                "rule": f"{from_p} must not depend on {bad_p}"
                            })

        return violations
