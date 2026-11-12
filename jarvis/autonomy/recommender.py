"""
Capability 111: Contextual Recommendations
Generates proactive, ranked recommendations based on real-time project context,
system telemetry, file changes, recent errors, and pending milestones.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional


@dataclass
class Recommendation:
    """Actionable proactive recommendation for the user or autonomous agent."""
    rec_id: str
    title: str
    category: str  # SAFETY, WORKFLOW, CODE, KNOWLEDGE, PERFORMANCE
    rationale: str
    priority: str  # HIGH, MEDIUM, LOW
    confidence: float  # 0.0 to 1.0
    action_type: str
    action_payload: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ContextualRecommender:
    """
    Capability 111: Contextual Recommender Engine.
    Monitors workspace indicators and formulates high-leverage next actions.
    """

    def __init__(self):
        pass

    def evaluate_context(self, context: Dict[str, Any]) -> List[Recommendation]:
        """
        Analyzes a context dictionary containing flags, telemetry, and pending state,
        returning prioritized and ranked recommendations.
        """
        recs: List[Recommendation] = []

        # 1. Error state / crash alerts
        recent_errors = context.get("recent_errors", [])
        if recent_errors:
            recs.append(Recommendation(
                rec_id=f"rec_{uuid.uuid4().hex[:6]}",
                title="Investigate Recent Runtime Failures",
                category="SAFETY",
                rationale=f"Detected {len(recent_errors)} recent error(s). Triaging now prevents cascade failures.",
                priority="HIGH",
                confidence=0.95,
                action_type="trigger_diagnostics",
                action_payload={"error_sample": recent_errors[-1] if recent_errors else None}
            ))

        # 2. Dirty git state / safety checkpoint
        if context.get("has_uncommitted_changes") or context.get("tasks_completed_count", 0) >= 3:
            recs.append(Recommendation(
                rec_id=f"rec_{uuid.uuid4().hex[:6]}",
                title="Create Safety Git Checkpoint",
                category="SAFETY",
                rationale="Significant changes have completed without a safety commit point.",
                priority="HIGH",
                confidence=0.88,
                action_type="git_checkpoint",
                action_payload={"message": "Auto-checkpoint prior to next execution phase"}
            ))

        # 3. High CPU or Memory Pressure
        cpu = context.get("cpu_percent", 0.0)
        ram = context.get("ram_percent", 0.0)
        if cpu > 80.0 or ram > 85.0:
            recs.append(Recommendation(
                rec_id=f"rec_{uuid.uuid4().hex[:6]}",
                title="Throttle Background Task Concurrency",
                category="PERFORMANCE",
                rationale=f"System under load (CPU: {cpu}%, RAM: {ram}%). Pacing workers avoids host unresponsiveness.",
                priority="HIGH",
                confidence=0.92,
                action_type="throttle_resources",
                action_payload={"throttle_level": "MODERATE"}
            ))

        # 4. Pending Knowledge / Note additions
        new_notes = context.get("new_notes_count", 0)
        if new_notes > 0:
            recs.append(Recommendation(
                rec_id=f"rec_{uuid.uuid4().hex[:6]}",
                title="Refresh Knowledge Graph & Indices",
                category="KNOWLEDGE",
                rationale=f"{new_notes} new note(s) detected. Re-indexing maintains grounding and 3D graph accuracy.",
                priority="MEDIUM",
                confidence=0.80,
                action_type="refresh_knowledge_graph",
                action_payload={"new_notes": new_notes}
            ))

        # 5. Untested code changes
        if context.get("untested_code_changes", False):
            recs.append(Recommendation(
                rec_id=f"rec_{uuid.uuid4().hex[:6]}",
                title="Execute Autonomous Unit Tests",
                category="CODE",
                rationale="New code modifications have not been verified by unit test runners.",
                priority="HIGH",
                confidence=0.90,
                action_type="run_unit_tests",
                action_payload={"target_suite": "tests/test_autonomy.py"}
            ))

        # 6. Idle swarm with pending tasks
        pending_tasks = context.get("pending_tasks_count", 0)
        if pending_tasks > 0 and context.get("active_workers_count", 0) == 0:
            recs.append(Recommendation(
                rec_id=f"rec_{uuid.uuid4().hex[:6]}",
                title="Dispatch Next Pending Task Batch",
                category="WORKFLOW",
                rationale=f"{pending_tasks} task(s) ready in DAG with idle capacity.",
                priority="MEDIUM",
                confidence=0.85,
                action_type="dispatch_tasks",
                action_payload={"count": pending_tasks}
            ))

        # Sort recommendations by priority and confidence
        prio_weights = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        recs.sort(key=lambda r: (prio_weights.get(r.priority, 1), r.confidence), reverse=True)
        return recs
