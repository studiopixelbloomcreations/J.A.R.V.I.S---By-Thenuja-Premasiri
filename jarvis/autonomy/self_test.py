"""
Capability 109: Self-Testing
Autonomous test harness for self-verification, synthetic smoke tests,
regression checking, and automated reporting.
"""
from __future__ import annotations

import io
import time
import unittest
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Callable


@dataclass
class TestCaseResult:
    """Individual test case execution metric."""
    name: str
    status: str  # PASS, FAIL, ERROR
    duration_seconds: float
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TestSummary:
    """Consolidated test execution results."""
    total: int
    passed: int
    failed: int
    errors: int
    duration_seconds: float
    pass_rate: float
    results: List[TestCaseResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "errors": self.errors,
            "duration_seconds": round(self.duration_seconds, 3),
            "pass_rate": round(self.pass_rate, 2),
            "results": [r.to_dict() for r in self.results]
        }

    def to_markdown(self) -> str:
        lines = [
            "# Self-Test Execution Summary",
            f"- **Total Tests:** {self.total}",
            f"- **Passed:** {self.passed} ({(self.pass_rate * 100):.1f}%)",
            f"- **Failed:** {self.failed}",
            f"- **Errors:** {self.errors}",
            f"- **Duration:** {self.duration_seconds:.3f}s",
            "",
            "## Test Details",
            "| Test Case | Status | Duration | Details |",
            "| :--- | :---: | :---: | :--- |"
        ]
        for r in self.results:
            badge = "PASSED" if r.status == "PASS" else "FAILED"
            err = r.error or "None"
            lines.append(f"| `{r.name}` | {badge} | {r.duration_seconds:.3f}s | {err} |")
        return "\n".join(lines)


class SelfTestRunner:
    """
    Capability 109: Autonomous Self-Testing Engine.
    Executes automated smoke checks on autonomy components to confirm sanity.
    """

    def __init__(self):
        pass

    def run_smoke_tests(self) -> TestSummary:
        """Runs the synthetic autonomy smoke test suite."""
        suite = [
            ("goal_decomposition_smoke", self._smoke_goal_decomposer),
            ("task_dag_toposort_smoke", self._smoke_task_dag),
            ("circuit_breaker_smoke", self._smoke_circuit_breaker),
            ("background_runner_smoke", self._smoke_background_manager),
        ]

        results: List[TestCaseResult] = []
        t0 = time.time()
        passed = 0
        failed = 0
        errors = 0

        for name, fn in suite:
            t_case_start = time.time()
            try:
                fn()
                dur = time.time() - t_case_start
                results.append(TestCaseResult(name=name, status="PASS", duration_seconds=dur))
                passed += 1
            except AssertionError as ae:
                dur = time.time() - t_case_start
                results.append(TestCaseResult(name=name, status="FAIL", duration_seconds=dur, error=str(ae)))
                failed += 1
            except Exception as e:
                dur = time.time() - t_case_start
                results.append(TestCaseResult(name=name, status="ERROR", duration_seconds=dur, error=str(e)))
                errors += 1

        total_dur = time.time() - t0
        total = len(suite)
        pass_rate = passed / total if total > 0 else 0.0

        return TestSummary(
            total=total,
            passed=passed,
            failed=failed,
            errors=errors,
            duration_seconds=total_dur,
            pass_rate=pass_rate,
            results=results
        )

    def _smoke_goal_decomposer(self):
        from .goal_decomposer import GoalDecomposer
        gd = GoalDecomposer()
        decomp = gd.decompose("Build a secure Python microservice with automated unit tests")
        assert len(decomp.sub_goals) >= 3, "Expected at least 3 sub-goals"
        assert decomp.goal_id.startswith("goal_"), "Expected goal ID prefix"

    def _smoke_task_dag(self):
        from .task_planner import TaskDAG, TaskNode
        dag = TaskDAG()
        dag.add_task(TaskNode(id="A", title="Node A"))
        dag.add_task(TaskNode(id="B", title="Node B", dependencies=["A"]))
        dag.add_task(TaskNode(id="C", title="Node C", dependencies=["B"]))
        order = dag.topological_sort()
        assert order == ["A", "B", "C"], f"Unexpected ordering: {order}"
        assert not dag.has_cycle(), "Should not detect cycle"

    def _smoke_circuit_breaker(self):
        from .recovery import CircuitBreaker, CircuitState
        cb = CircuitBreaker(name="test_cb", failure_threshold=2, recovery_timeout=0.1)
        assert cb.allow_request() is True
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.allow_request() is False

    def _smoke_background_manager(self):
        from .background_manager import BackgroundTaskManager, BackgroundStatus
        bm = BackgroundTaskManager(max_workers=2)
        try:
            tid = bm.submit("add", lambda x, y: x + y, 10, 20)
            res = bm.get_result(tid, wait=True, timeout=2.0)
            assert res == 30, f"Expected 30, got {res}"
            status = bm.get_status(tid)
            assert status["status"] == BackgroundStatus.COMPLETED.value
        finally:
            bm.shutdown(wait=False)
