"""
Capability 110: Workflow Optimization
Analyzes task execution DAGs, identifies critical path bottlenecks, discovers
parallelization opportunities, eliminates redundant steps, and computes speedups.
"""
from __future__ import annotations

import collections
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Set, Any, Optional, Tuple

from .task_planner import TaskDAG, TaskNode


@dataclass
class OptimizationSuggestion:
    """A prescriptive recommendation to accelerate workflow execution."""
    suggestion_type: str  # PARALLELIZE, BOTTLENECK_SPLIT, REDUNDANT_ELIMINATION
    description: str
    affected_tasks: List[str]
    estimated_seconds_saved: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OptimizationReport:
    """Complete optimization analysis and projected gains."""
    original_sequential_seconds: int
    parallel_critical_path_seconds: int
    projected_optimized_seconds: int
    speedup_factor: float
    bottleneck_tasks: List[str]
    suggestions: List[OptimizationSuggestion] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_sequential_seconds": self.original_sequential_seconds,
            "parallel_critical_path_seconds": self.parallel_critical_path_seconds,
            "projected_optimized_seconds": self.projected_optimized_seconds,
            "speedup_factor": round(self.speedup_factor, 2),
            "bottleneck_tasks": self.bottleneck_tasks,
            "suggestions": [s.to_dict() for s in self.suggestions]
        }


class WorkflowOptimizer:
    """
    Capability 110: Autonomous Workflow Optimizer.
    Inspects execution graphs to maximize throughput and minimize latency.
    """

    def __init__(self):
        pass

    def optimize_dag(self, dag: TaskDAG) -> OptimizationReport:
        """Analyzes a TaskDAG, detects inefficiencies, and projects acceleration."""
        if not dag.tasks:
            return OptimizationReport(0, 0, 0, 1.0, [])

        # Sequential baseline (sum of all durations)
        total_seq = sum(t.duration_estimate_seconds for t in dag.tasks.values())

        # Parallel baseline (current critical path)
        crit_path, crit_duration = dag.find_critical_path()

        suggestions: List[OptimizationSuggestion] = []
        bottlenecks: List[str] = []

        # 1. Bottleneck detection (any task >= 35% of critical path)
        for tid in crit_path:
            t = dag.tasks[tid]
            if crit_duration > 0 and (t.duration_estimate_seconds / crit_duration) >= 0.35:
                bottlenecks.append(tid)
                saved = int(t.duration_estimate_seconds * 0.4)
                suggestions.append(OptimizationSuggestion(
                    suggestion_type="BOTTLENECK_SPLIT",
                    description=f"Task '{t.title}' ({tid}) accounts for {(t.duration_estimate_seconds/crit_duration)*100:.1f}% of critical path. Split into sub-tasks.",
                    affected_tasks=[tid],
                    estimated_seconds_saved=saved
                ))

        # 2. Redundancy detection (tasks with duplicate titles/descriptions)
        seen_titles: Dict[str, str] = {}
        for tid, t in dag.tasks.items():
            norm_title = t.title.lower().strip()
            if norm_title in seen_titles:
                first_tid = seen_titles[norm_title]
                suggestions.append(OptimizationSuggestion(
                    suggestion_type="REDUNDANT_ELIMINATION",
                    description=f"Task '{t.title}' ({tid}) appears identical to earlier task {first_tid}. Cache result and reuse.",
                    affected_tasks=[tid, first_tid],
                    estimated_seconds_saved=t.duration_estimate_seconds
                ))
            else:
                seen_titles[norm_title] = tid

        # 3. Parallelization opportunities across tiers
        tiers = dag.get_parallel_tiers()
        for i, tier in enumerate(tiers):
            if len(tier) > 1:
                tier_tasks = [dag.tasks[tid].title for tid in tier]
                suggestions.append(OptimizationSuggestion(
                    suggestion_type="PARALLELIZE",
                    description=f"Tier {i} contains {len(tier)} independent tasks that can execute concurrently: {', '.join(tier_tasks)}.",
                    affected_tasks=tier,
                    estimated_seconds_saved=max(0, sum(dag.tasks[tid].duration_estimate_seconds for tid in tier) - max(dag.tasks[tid].duration_estimate_seconds for tid in tier))
                ))

        # Projected optimized time
        total_saved_from_bottlenecks = sum(
            s.estimated_seconds_saved for s in suggestions if s.suggestion_type == "BOTTLENECK_SPLIT"
        )
        projected = max(1, crit_duration - total_saved_from_bottlenecks)
        speedup = total_seq / projected if projected > 0 else 1.0

        return OptimizationReport(
            original_sequential_seconds=total_seq,
            parallel_critical_path_seconds=crit_duration,
            projected_optimized_seconds=projected,
            speedup_factor=speedup,
            bottleneck_tasks=bottlenecks,
            suggestions=suggestions
        )
