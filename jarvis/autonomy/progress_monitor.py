"""
Capability 106: Progress Monitoring
Tracks real-time task progression, milestone completions, execution velocity,
and estimated time to completion (ETA).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Set, Any, Optional, Callable


@dataclass
class Milestone:
    """Represents a milestone composed of multiple required prerequisite tasks."""
    id: str
    title: str
    required_tasks: List[str]
    completed: bool = False
    completed_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "required_tasks": self.required_tasks,
            "completed": self.completed,
            "completed_at": self.completed_at
        }


@dataclass
class TrackedTask:
    """Internal tracking record for a task."""
    task_id: str
    weight: float = 1.0
    progress: float = 0.0  # 0.0 to 1.0
    status: str = "PENDING"
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


class ProgressMonitor:
    """
    Capability 106: Progress Monitor.
    Provides fine-grained velocity tracking, ETA projections, and milestone verification.
    """

    def __init__(self, workflow_name: str = "Workflow"):
        self.workflow_name = workflow_name
        self.tasks: Dict[str, TrackedTask] = {}
        self.milestones: Dict[str, Milestone] = {}
        self.started_at: float = time.time()
        self._listeners: List[Callable[[Dict[str, Any]], None]] = []

    def register_task(self, task_id: str, weight: float = 1.0) -> None:
        """Registers a task for progress tracking."""
        self.tasks[task_id] = TrackedTask(task_id=task_id, weight=weight)

    def add_milestone(self, milestone_id: str, title: str, required_tasks: List[str]) -> None:
        """Adds a project milestone requiring specified tasks to be 100% complete."""
        self.milestones[milestone_id] = Milestone(
            id=milestone_id,
            title=title,
            required_tasks=required_tasks
        )

    def add_listener(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Subscribes an event listener for progress updates."""
        self._listeners.append(callback)

    def update_task(self, task_id: str, progress: float, status: str = "RUNNING") -> Dict[str, Any]:
        """
        Updates task progress fraction (0.0 to 1.0) and status.
        Triggers milestone checks and notifies registered listeners.
        """
        if task_id not in self.tasks:
            self.register_task(task_id)

        task = self.tasks[task_id]
        task.progress = max(0.0, min(1.0, progress))
        task.status = status

        if task.progress > 0 and task.started_at is None:
            task.started_at = time.time()
        if task.progress >= 1.0 or status == "COMPLETED":
            task.progress = 1.0
            task.status = "COMPLETED"
            if task.completed_at is None:
                task.completed_at = time.time()

        # Check milestones
        newly_achieved = self._evaluate_milestones()

        summary = self.get_summary()
        summary["updated_task"] = task_id
        summary["newly_achieved_milestones"] = newly_achieved

        for cb in self._listeners:
            try:
                cb(summary)
            except Exception:
                pass

        return summary

    def _evaluate_milestones(self) -> List[str]:
        """Checks if any uncompleted milestones have now been achieved."""
        achieved = []
        for mid, m in self.milestones.items():
            if not m.completed:
                if all(self.tasks.get(tid) and self.tasks[tid].status == "COMPLETED" for tid in m.required_tasks):
                    m.completed = True
                    m.completed_at = time.time()
                    achieved.append(mid)
        return achieved

    def get_completion_percentage(self) -> float:
        """Calculates total weighted percentage (0.0 to 100.0)."""
        if not self.tasks:
            return 0.0
        total_weight = sum(t.weight for t in self.tasks.values())
        if total_weight <= 0:
            return 0.0
        weighted_progress = sum(t.progress * t.weight for t in self.tasks.values())
        return round((weighted_progress / total_weight) * 100.0, 2)

    def estimate_eta_seconds(self) -> Optional[float]:
        """Estimates remaining time in seconds based on current velocity."""
        pct = self.get_completion_percentage()
        if pct <= 0.0:
            return None
        if pct >= 100.0:
            return 0.0

        elapsed = time.time() - self.started_at
        if elapsed <= 0:
            return None

        # Velocity in pct per second
        velocity = pct / elapsed
        if velocity <= 0:
            return None
        remaining_pct = 100.0 - pct
        return round(remaining_pct / velocity, 1)

    def get_summary(self) -> Dict[str, Any]:
        """Provides comprehensive snapshot of execution status."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == "COMPLETED")
        running = sum(1 for t in self.tasks.values() if t.status == "RUNNING")
        pending = sum(1 for t in self.tasks.values() if t.status == "PENDING")
        failed = sum(1 for t in self.tasks.values() if t.status == "FAILED")

        pct = self.get_completion_percentage()
        eta = self.estimate_eta_seconds()

        return {
            "workflow_name": self.workflow_name,
            "completion_percentage": pct,
            "eta_seconds": eta,
            "tasks_count": {
                "total": total,
                "completed": completed,
                "running": running,
                "pending": pending,
                "failed": failed
            },
            "milestones": {mid: m.to_dict() for mid, m in self.milestones.items()}
        }
