"""
Capability 102: Autonomous Task Planning
Constructs Directed Acyclic Graphs (DAGs) of tasks, performs topological sorting,
detects cycles, calculates critical paths, groups tasks into parallel execution tiers,
and dynamically generates execution plans.
"""
from __future__ import annotations

import collections
import enum
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Set, Any, Optional, Tuple

from .goal_decomposer import DecomposedGoal, SubGoal


class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"


@dataclass
class TaskNode:
    """A single node within a task dependency graph."""
    id: str
    title: str
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    duration_estimate_seconds: int = 60
    priority: int = 5  # 1 (lowest) to 10 (highest)
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value if isinstance(self.status, TaskStatus) else str(self.status)
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TaskNode:
        data = dict(data)
        if "status" in data and isinstance(data["status"], str):
            data["status"] = TaskStatus(data["status"])
        return cls(**data)


class TaskDAG:
    """Directed Acyclic Graph representing task dependencies."""

    def __init__(self):
        self.tasks: Dict[str, TaskNode] = {}
        self.adj_list: Dict[str, Set[str]] = collections.defaultdict(set)  # parent -> children
        self.in_degree: Dict[str, int] = collections.defaultdict(int)

    def add_task(self, task: TaskNode) -> None:
        """Adds a task node to the DAG."""
        self.tasks[task.id] = task
        if task.id not in self.adj_list:
            self.adj_list[task.id] = set()
        if task.id not in self.in_degree:
            self.in_degree[task.id] = 0

        # Register incoming dependencies
        for dep_id in task.dependencies:
            self.add_dependency(child_id=task.id, parent_id=dep_id)

    def add_dependency(self, child_id: str, parent_id: str) -> None:
        """Declares that child_id depends on parent_id."""
        if parent_id not in self.tasks:
            # Placeholder node if not yet added
            self.tasks[parent_id] = TaskNode(id=parent_id, title=parent_id)
        if child_id not in self.tasks:
            self.tasks[child_id] = TaskNode(id=child_id, title=child_id)

        if parent_id not in self.tasks[child_id].dependencies:
            self.tasks[child_id].dependencies.append(parent_id)

        if child_id not in self.adj_list[parent_id]:
            self.adj_list[parent_id].add(child_id)
            self.in_degree[child_id] = self.in_degree.get(child_id, 0) + 1

    def has_cycle(self) -> bool:
        """Determines if there is a circular dependency in the graph using 3-color DFS."""
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {tid: WHITE for tid in self.tasks}

        def dfs(node: str) -> bool:
            color[node] = GRAY
            for child in self.adj_list.get(node, []):
                if color.get(child, WHITE) == GRAY:
                    return True
                if color.get(child, WHITE) == WHITE and dfs(child):
                    return True
            color[node] = BLACK
            return False

        for node in list(self.tasks.keys()):
            if color.get(node, WHITE) == WHITE:
                if dfs(node):
                    return True
        return False

    def topological_sort(self) -> List[str]:
        """
        Returns linear task execution ordering using Kahn's algorithm.
        Raises ValueError if circular dependency detected.
        """
        if self.has_cycle():
            raise ValueError("Task graph contains a cycle; cannot perform topological sort.")

        in_deg = {tid: len(self.tasks[tid].dependencies) for tid in self.tasks}
        queue = collections.deque([tid for tid, deg in in_deg.items() if deg == 0])
        # Sort queue by priority descending for deterministic and high-priority scheduling
        order: List[str] = []

        while queue:
            # Sort current level by priority descending
            sorted_level = sorted(queue, key=lambda tid: self.tasks[tid].priority, reverse=True)
            curr = sorted_level[0]
            queue.remove(curr)
            order.append(curr)

            for child in self.adj_list.get(curr, []):
                in_deg[child] -= 1
                if in_deg[child] == 0:
                    queue.append(child)

        if len(order) != len(self.tasks):
            raise ValueError("Cycle detected during topological sorting.")
        return order

    def get_parallel_tiers(self) -> List[List[str]]:
        """
        Groups tasks into sequential tiers where all tasks in a tier can run concurrently.
        Tier 0 contains tasks with no dependencies.
        Tier k contains tasks whose dependencies are all satisfied by tiers < k.
        """
        if self.has_cycle():
            raise ValueError("Cycle detected; cannot compute parallel tiers.")

        tier_map: Dict[str, int] = {}
        sorted_nodes = self.topological_sort()

        for tid in sorted_nodes:
            deps = self.tasks[tid].dependencies
            if not deps:
                tier_map[tid] = 0
            else:
                max_dep_tier = max(tier_map[d] for d in deps if d in tier_map)
                tier_map[tid] = max_dep_tier + 1

        max_tier = max(tier_map.values()) if tier_map else -1
        tiers: List[List[str]] = [[] for _ in range(max_tier + 1)]
        for tid, tier in tier_map.items():
            tiers[tier].append(tid)

        # Sort tasks within each tier by priority descending
        for i in range(len(tiers)):
            tiers[i].sort(key=lambda tid: self.tasks[tid].priority, reverse=True)

        return tiers

    def find_critical_path(self) -> Tuple[List[str], int]:
        """
        Computes the critical path (longest duration path from root to leaf) and its duration.
        Returns (list_of_task_ids, total_duration_seconds).
        """
        if not self.tasks:
            return [], 0
        if self.has_cycle():
            raise ValueError("Cycle detected; cannot find critical path.")

        sorted_nodes = self.topological_sort()
        dist: Dict[str, int] = {}
        prev: Dict[str, Optional[str]] = {}

        for tid in sorted_nodes:
            duration = self.tasks[tid].duration_estimate_seconds
            deps = self.tasks[tid].dependencies
            if not deps:
                dist[tid] = duration
                prev[tid] = None
            else:
                # Find max distance parent
                best_parent = None
                max_parent_dist = -1
                for d in deps:
                    if dist.get(d, 0) > max_parent_dist:
                        max_parent_dist = dist[d]
                        best_parent = d
                dist[tid] = max_parent_dist + duration
                prev[tid] = best_parent

        # Find terminal node with maximum distance
        end_node = max(dist.keys(), key=lambda k: dist[k])
        total_duration = dist[end_node]

        # Reconstruct path
        path = []
        curr = end_node
        while curr:
            path.append(curr)
            curr = prev.get(curr)
        path.reverse()
        return path, total_duration

    def get_ready_tasks(self, completed_ids: Set[str]) -> List[TaskNode]:
        """Returns pending tasks whose prerequisites are completely satisfied."""
        ready = []
        for tid, task in self.tasks.items():
            if task.status in (TaskStatus.PENDING, TaskStatus.READY):
                deps_satisfied = all(d in completed_ids for d in task.dependencies)
                if deps_satisfied:
                    task.status = TaskStatus.READY
                    ready.append(task)
                else:
                    task.status = TaskStatus.BLOCKED
        ready.sort(key=lambda t: t.priority, reverse=True)
        return ready

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tasks": {tid: task.to_dict() for tid, task in self.tasks.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TaskDAG:
        dag = cls()
        tasks_data = data.get("tasks", {})
        for tid, tdict in tasks_data.items():
            task = TaskNode.from_dict(tdict)
            dag.add_task(task)
        return dag


@dataclass
class ExecutionPlan:
    """An executable multi-tier plan derived from a TaskDAG."""
    plan_id: str
    dag: TaskDAG
    parallel_tiers: List[List[str]]
    critical_path: List[str]
    total_estimated_duration: int
    created_at: float = field(default_factory=time.time)

    def summary(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "total_tasks": len(self.dag.tasks),
            "total_tiers": len(self.parallel_tiers),
            "critical_path": self.critical_path,
            "total_estimated_duration_sec": self.total_estimated_duration,
            "parallel_tiers": self.parallel_tiers
        }


class TaskPlanner:
    """
    Capability 102: Autonomous Task Planner.
    Converts goals and task definitions into execution plans with dependency resolution,
    cycle prevention, priority scheduling, and adaptive replanning.
    """

    def __init__(self):
        pass

    def plan_from_decomposed_goal(self, goal: DecomposedGoal) -> ExecutionPlan:
        """Transforms a DecomposedGoal into an optimized ExecutionPlan."""
        dag = TaskDAG()
        for sg in goal.sub_goals:
            priority_map = {"high": 8, "medium": 5, "low": 3}
            task = TaskNode(
                id=sg.id,
                title=sg.title,
                description=sg.description,
                dependencies=list(sg.dependencies),
                duration_estimate_seconds=sg.estimated_seconds,
                priority=priority_map.get(sg.estimated_complexity.lower(), 5),
                inputs=sg.inputs,
                outputs=sg.expected_outputs,
                metadata={
                    "phase": sg.phase,
                    "risk_level": sg.risk_level,
                    "acceptance_criteria": sg.acceptance_criteria
                }
            )
            dag.add_task(task)

        parallel_tiers = dag.get_parallel_tiers()
        crit_path, duration = dag.find_critical_path()
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"

        return ExecutionPlan(
            plan_id=plan_id,
            dag=dag,
            parallel_tiers=parallel_tiers,
            critical_path=crit_path,
            total_estimated_duration=duration
        )

    def plan_from_tasks(self, tasks: List[TaskNode]) -> ExecutionPlan:
        """Generates an ExecutionPlan from an explicit list of TaskNodes."""
        dag = TaskDAG()
        for t in tasks:
            dag.add_task(t)

        parallel_tiers = dag.get_parallel_tiers()
        crit_path, duration = dag.find_critical_path()
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"

        return ExecutionPlan(
            plan_id=plan_id,
            dag=dag,
            parallel_tiers=parallel_tiers,
            critical_path=crit_path,
            total_estimated_duration=duration
        )

    def replan_on_failure(self, dag: TaskDAG, failed_task_id: str,
                          fallback_task: Optional[TaskNode] = None) -> ExecutionPlan:
        """
        Dynamically adjusts DAG upon task failure by injecting fallback mitigations
        or pruning affected downstream branches.
        """
        if failed_task_id in dag.tasks:
            dag.tasks[failed_task_id].status = TaskStatus.FAILED

        if fallback_task:
            dag.add_task(fallback_task)
            # Re-point children of failed_task to fallback_task
            children = list(dag.adj_list.get(failed_task_id, []))
            for ch in children:
                dag.add_dependency(child_id=ch, parent_id=fallback_task.id)

        tiers = dag.get_parallel_tiers()
        crit_path, duration = dag.find_critical_path()
        return ExecutionPlan(
            plan_id=f"plan_recovery_{uuid.uuid4().hex[:8]}",
            dag=dag,
            parallel_tiers=tiers,
            critical_path=crit_path,
            total_estimated_duration=duration
        )
