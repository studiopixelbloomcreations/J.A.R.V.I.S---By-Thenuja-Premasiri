"""
Capability 115: Autonomous Documentation
Auto-generates comprehensive Markdown run summaries, post-mortem incident reports,
Mermaid DAG flowcharts, and milestone documentation saved directly to knowledge archives.
"""
from __future__ import annotations

import os
import pathlib
import time
from typing import Dict, List, Any, Optional

from ..config import NOTES_DIR
from .task_planner import TaskDAG, TaskStatus


class AutonomousDocumenter:
    """
    Capability 115: Autonomous Documentation Engine.
    Transforms execution telemetry and graph structures into human-readable, auditable docs.
    """

    def __init__(self, notes_dir: Optional[pathlib.Path] = None):
        self.notes_dir = notes_dir or NOTES_DIR
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    def generate_dag_mermaid(self, dag: TaskDAG) -> str:
        """Generates Mermaid flowchart diagram for the task graph."""
        lines = ["```mermaid", "flowchart TD"]
        for tid, task in dag.tasks.items():
            status_symbol = {
                TaskStatus.COMPLETED: " [Done]",
                TaskStatus.RUNNING: " [Running]",
                TaskStatus.FAILED: " [Failed]",
                TaskStatus.BLOCKED: " [Blocked]",
                TaskStatus.PENDING: " [Pending]"
            }.get(task.status, "")
            safe_title = task.title.replace('"', "'")
            lines.append(f'    {tid}["{safe_title}{status_symbol}"]')

        for parent, children in dag.adj_list.items():
            for child in children:
                lines.append(f"    {parent} --> {child}")

        lines.append("```")
        return "\n".join(lines)

    def generate_execution_report(self, workflow_name: str, dag: TaskDAG,
                                  execution_summary: Optional[Dict[str, Any]] = None) -> str:
        """Compiles a complete execution dossier with Mermaid graph, task table, and metrics."""
        summary = execution_summary or {}
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        mermaid_block = self.generate_dag_mermaid(dag)

        total_tasks = len(dag.tasks)
        completed = sum(1 for t in dag.tasks.values() if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in dag.tasks.values() if t.status == TaskStatus.FAILED)
        duration_est = sum(t.duration_estimate_seconds for t in dag.tasks.values())

        lines = [
            f"# Autonomous Workflow Execution Report: {workflow_name}",
            f"- **Generated:** `{timestamp_str}`",
            f"- **Total Tasks:** {total_tasks}",
            f"- **Completed:** {completed}",
            f"- **Failed:** {failed}",
            f"- **Total Estimated Duration:** {duration_est}s",
            "",
            "## Task Dependency Graph",
            mermaid_block,
            "",
            "## Task Breakdown",
            "| Task ID | Title | Priority | Est Duration | Status | Error |",
            "| :--- | :--- | :---: | :---: | :---: | :--- |"
        ]

        for tid, t in dag.tasks.items():
            err = t.error or "None"
            lines.append(f"| `{tid}` | {t.title} | {t.priority} | {t.duration_estimate_seconds}s | `{t.status.value}` | {err} |")

        if summary:
            lines.extend([
                "",
                "## Execution Telemetry",
                f"- **Actual Duration:** {summary.get('actual_duration_seconds', 'N/A')}s",
                f"- **Peak Concurrency:** {summary.get('peak_concurrency', 1)}",
                f"- **CPU Throttle Level:** `{summary.get('throttle_level', 'NORMAL')}`",
            ])

        return "\n".join(lines)

    def generate_post_mortem(self, workflow_name: str, failed_task_id: str,
                             error_message: str, recovery_events: List[Dict[str, Any]]) -> str:
        """Builds a structured post-mortem incident report."""
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        lines = [
            f"# Incident Post-Mortem: {workflow_name}",
            f"- **Incident Timestamp:** `{timestamp_str}`",
            f"- **Failed Task ID:** `{failed_task_id}`",
            f"- **Root Error Message:** `{error_message}`",
            "",
            "## Recovery Timeline & Actions",
            "| Time | Action | Outcome | Detail |",
            "| :--- | :--- | :--- | :--- |"
        ]

        for ev in recovery_events:
            t_str = time.strftime("%H:%M:%S", time.localtime(ev.get("timestamp", time.time())))
            lines.append(f"| {t_str} | {ev.get('action')} | `{ev.get('outcome')}` | {ev.get('detail')} |")

        lines.extend([
            "",
            "## Corrective Directives",
            "1. Verify input data integrity before dispatching downstream tasks.",
            "2. Keep circuit breakers active to isolate transient network/storage errors.",
            "3. Resume execution from the last valid checkpoint once fault is remediated."
        ])

        return "\n".join(lines)

    def save_report(self, filename: str, content: str) -> pathlib.Path:
        """Persists Markdown report to notes archive."""
        if not filename.endswith(".md"):
            filename = f"{filename}.md"
        out_path = self.notes_dir / filename
        out_path.write_text(content, encoding="utf-8")
        return out_path
