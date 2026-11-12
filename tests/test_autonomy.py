"""
Comprehensive Unit Tests for J.A.R.V.I.S. Autonomy Subsystem
Validates Capabilities 101-115:
101. Goal Decomposition
102. Autonomous Task Planning
103. Multi-Agent Orchestration
104. Background Task Management
105. Scheduled Research
106. Progress Monitoring
107. Failure Recovery
108. Self-Diagnostics
109. Self-Testing
110. Workflow Optimization
111. Contextual Recommendations
112. Event Monitoring
113. Task Continuity (Checkpoint & state resumption)
114. Resource Awareness (CPU/memory throttling)
115. Autonomous Documentation
"""

import os
import sys
import time
import shutil
import pathlib
import tempfile
import unittest

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = pathlib.Path(__file__).parent.parent.resolve()
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from jarvis.autonomy.goal_decomposer import GoalDecomposer, DecomposedGoal, SubGoal
from jarvis.autonomy.task_planner import TaskPlanner, TaskDAG, TaskNode, TaskStatus, ExecutionPlan
from jarvis.autonomy.multi_agent import (
    MultiAgentOrchestrator, AgentWorker, AgentRole, AgentState, AgentMessage
)
from jarvis.autonomy.background_manager import BackgroundTaskManager, BackgroundStatus
from jarvis.autonomy.scheduler import AutonomousScheduler, ScheduledJob
from jarvis.autonomy.progress_monitor import ProgressMonitor, Milestone
from jarvis.autonomy.recovery import (
    FailureRecoveryManager, RetryPolicy, CircuitBreaker, CircuitState,
    classify_error, ErrorCategory
)
from jarvis.autonomy.diagnostics import SelfDiagnostics, HealthReport
from jarvis.autonomy.self_test import SelfTestRunner, TestSummary
from jarvis.autonomy.optimizer import WorkflowOptimizer
from jarvis.autonomy.recommender import ContextualRecommender
from jarvis.autonomy.event_bus import AutonomousEventBus, Event
from jarvis.autonomy.checkpoint import CheckpointManager, CheckpointRecord
from jarvis.autonomy.resource_guard import ResourceGuard, ThrottleLevel, ResourceMetrics
from jarvis.autonomy.documenter import AutonomousDocumenter
from jarvis.autonomy import AutonomousEngine, CAPABILITIES_MAP


class TestGoalDecomposition(unittest.TestCase):
    """Capability 101: Goal Decomposition"""

    def setUp(self):
        self.decomposer = GoalDecomposer()

    def test_software_decomposition(self):
        goal = "Build a high-performance Python caching service with unit tests"
        decomp = self.decomposer.decompose(goal)
        self.assertIsInstance(decomp, DecomposedGoal)
        self.assertTrue(decomp.goal_id.startswith("goal_"))
        self.assertEqual(decomp.metadata["domain"], "software")
        self.assertGreaterEqual(len(decomp.sub_goals), 4)

        # Check dependency ordering
        sub_ids = [sg.id for sg in decomp.sub_goals]
        self.assertIn("sg_arch", sub_ids)
        self.assertIn("sg_impl", sub_ids)
        impl_goal = next(sg for sg in decomp.sub_goals if sg.id == "sg_impl")
        self.assertIn("sg_arch", impl_goal.dependencies)

    def test_research_decomposition(self):
        goal = "Research and investigate quantum error correction papers"
        decomp = self.decomposer.decompose(goal)
        self.assertEqual(decomp.metadata["domain"], "research")
        self.assertGreaterEqual(len(decomp.sub_goals), 3)

    def test_security_decomposition(self):
        goal = "Perform an authorized vulnerability audit of local network ports"
        decomp = self.decomposer.decompose(goal)
        self.assertEqual(decomp.metadata["domain"], "security")
        self.assertGreaterEqual(len(decomp.sub_goals), 3)

    def test_markdown_plan_generation(self):
        goal = "Deploy a backup daemon without system downtime"
        decomp = self.decomposer.decompose(goal)
        md = decomp.to_markdown_plan()
        self.assertIn("# Execution Plan", md)
        self.assertIn("Acceptance Criteria", md)
        self.assertIn("Avoid: system downtime", md)


class TestAutonomousTaskPlanning(unittest.TestCase):
    """Capability 102: Autonomous Task Planning"""

    def setUp(self):
        self.planner = TaskPlanner()

    def test_dag_topological_sort_and_tiers(self):
        dag = TaskDAG()
        dag.add_task(TaskNode(id="T1", title="Init Schema", duration_estimate_seconds=10, priority=8))
        dag.add_task(TaskNode(id="T2", title="Seed Data", dependencies=["T1"], duration_estimate_seconds=20, priority=5))
        dag.add_task(TaskNode(id="T3", title="Compile Assets", dependencies=["T1"], duration_estimate_seconds=15, priority=6))
        dag.add_task(TaskNode(id="T4", title="Run Integration Tests", dependencies=["T2", "T3"], duration_estimate_seconds=30, priority=9))

        self.assertFalse(dag.has_cycle())
        order = dag.topological_sort()
        self.assertEqual(order[0], "T1")
        self.assertEqual(order[-1], "T4")

        tiers = dag.get_parallel_tiers()
        self.assertEqual(len(tiers), 3)
        self.assertEqual(tiers[0], ["T1"])
        self.assertIn("T2", tiers[1])
        self.assertIn("T3", tiers[1])
        self.assertEqual(tiers[2], ["T4"])

    def test_dag_cycle_detection(self):
        dag = TaskDAG()
        dag.add_task(TaskNode(id="A", title="Node A", dependencies=["C"]))
        dag.add_task(TaskNode(id="B", title="Node B", dependencies=["A"]))
        dag.add_task(TaskNode(id="C", title="Node C", dependencies=["B"]))

        self.assertTrue(dag.has_cycle())
        with self.assertRaises(ValueError):
            dag.topological_sort()

    def test_critical_path_calculation(self):
        dag = TaskDAG()
        dag.add_task(TaskNode(id="N1", title="Start", duration_estimate_seconds=10))
        dag.add_task(TaskNode(id="N2_Short", title="Quick Branch", dependencies=["N1"], duration_estimate_seconds=5))
        dag.add_task(TaskNode(id="N2_Long", title="Heavy Branch", dependencies=["N1"], duration_estimate_seconds=40))
        dag.add_task(TaskNode(id="N3", title="End", dependencies=["N2_Short", "N2_Long"], duration_estimate_seconds=15))

        path, duration = dag.find_critical_path()
        self.assertEqual(path, ["N1", "N2_Long", "N3"])
        self.assertEqual(duration, 65)

    def test_plan_from_decomposed_goal(self):
        decomposer = GoalDecomposer()
        decomp = decomposer.decompose("Build test suite")
        plan = self.planner.plan_from_decomposed_goal(decomp)
        self.assertIsInstance(plan, ExecutionPlan)
        self.assertGreater(len(plan.parallel_tiers), 0)
        self.assertGreater(plan.total_estimated_duration, 0)


class TestMultiAgentOrchestration(unittest.TestCase):
    """Capability 103: Multi-Agent Orchestration"""

    def setUp(self):
        self.orchestrator = MultiAgentOrchestrator()
        self.orchestrator.register_agent(AgentWorker(
            agent_id="ag_1", name="architect", role=AgentRole.ARCHITECT, capabilities=["design", "uml"]
        ))
        self.orchestrator.register_agent(AgentWorker(
            agent_id="ag_2", name="coder", role=AgentRole.CODER, capabilities=["python", "refactor"]
        ))
        self.orchestrator.register_agent(AgentWorker(
            agent_id="ag_3", name="tester", role=AgentRole.TESTER, capabilities=["unittest", "pytest"]
        ))

    def test_roster_and_routing(self):
        roster = self.orchestrator.get_roster()
        self.assertEqual(len(roster), 3)

        # Message routing
        msg = self.orchestrator.post_message(
            sender="coordinator",
            recipient="@coder",
            content="Please review module.py",
            msg_type="TASK_ASSIGN"
        )
        self.assertEqual(msg.recipient, "@coder")

        inbox = self.orchestrator.read_inbox("coder")
        self.assertEqual(len(inbox), 1)
        self.assertEqual(inbox[0].content, "Please review module.py")

        # Empty after reading with clear=True
        self.assertEqual(len(self.orchestrator.read_inbox("coder")), 0)

    def test_agent_task_assignment_and_handoff(self):
        self.orchestrator.assign_task("coder", "task_101", "Implement caching logic")
        coder = self.orchestrator.get_agent("coder")
        self.assertEqual(coder.state, AgentState.WORKING)
        self.assertEqual(coder.assigned_task_id, "task_101")

        # Handoff to tester
        self.orchestrator.handoff(from_agent="coder", to_agent="tester", task_id="task_101", artifact={"code": "cache.py"})
        self.assertEqual(coder.state, AgentState.IDLE)
        tester = self.orchestrator.get_agent("tester")
        self.assertEqual(tester.state, AgentState.WORKING)
        self.assertEqual(tester.assigned_task_id, "task_101")

    def test_consensus_voting(self):
        poll = self.orchestrator.conduct_voting(
            topic="Deploy Release Candidate",
            options=["approve", "require_testing", "reject"]
        )
        self.assertIn("winner", poll)
        self.assertIn("consensus_ratio", poll)
        self.assertEqual(poll["total_voters"], 3)

    def test_result_aggregation(self):
        subtasks = {
            "sub_1": {"status": "success", "data": "auth_ok"},
            "sub_2": {"status": "success", "data": "cache_ok"},
            "sub_3": {"status": "failed", "error": "timeout connecting to db"}
        }
        res = self.orchestrator.aggregate_results(subtasks)
        self.assertEqual(res["total_subtasks"], 3)
        self.assertEqual(res["successful_subtasks"], 2)
        self.assertEqual(res["failed_subtasks"], 1)
        self.assertAlmostEqual(res["success_rate"], 2/3, places=2)


class TestBackgroundTaskManagement(unittest.TestCase):
    """Capability 104: Background Task Management"""

    def setUp(self):
        self.bg = BackgroundTaskManager(max_workers=2)

    def tearDown(self):
        self.bg.shutdown(wait=False)

    def test_task_submission_and_completion(self):
        def sample_work(a, b):
            return a * b

        tid = self.bg.submit("multiply", sample_work, 6, 7)
        res = self.bg.get_result(tid, wait=True, timeout=3.0)
        self.assertEqual(res, 42)

        status = self.bg.get_status(tid)
        self.assertEqual(status["status"], BackgroundStatus.COMPLETED.value)
        self.assertEqual(status["progress"], 1.0)

    def test_task_progress_update(self):
        def slow_step():
            time.sleep(0.05)
            return "ok"

        tid = self.bg.submit("step_job", slow_step)
        self.bg.set_progress(tid, 0.5, "Halfway done")
        status = self.bg.get_status(tid)
        self.assertEqual(status["progress"], 0.5)
        self.assertEqual(status["progress_message"], "Halfway done")
        self.bg.get_result(tid, wait=True, timeout=2.0)

    def test_task_cancellation(self):
        def cancellable_job():
            time.sleep(0.5)
            return "done"

        tid = self.bg.submit("cancel_me", cancellable_job)
        self.assertTrue(self.bg.cancel_task(tid))
        status = self.bg.get_status(tid)
        self.assertIn(status["status"], [BackgroundStatus.CANCELLED.value, BackgroundStatus.RUNNING.value])


class TestScheduledResearch(unittest.TestCase):
    """Capability 105: Scheduled Research"""

    def setUp(self):
        self.scheduler = AutonomousScheduler()

    def test_interval_scheduling_and_tick(self):
        counter = {"count": 0}

        def increment():
            counter["count"] += 1
            return counter["count"]

        job_id = self.scheduler.schedule_interval("inc_job", interval_seconds=10.0, fn=increment)
        job = self.scheduler.get_job(job_id)
        self.assertEqual(job["name"], "inc_job")

        # Trigger tick at future timestamp
        now = time.time()
        results = self.scheduler.tick(current_time=now + 15.0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["success"], True)
        self.assertEqual(counter["count"], 1)

    def test_research_sweep_schedule(self):
        job_id = self.scheduler.schedule_research("Transformer Attention Mechanisms", interval_seconds=3600.0)
        job = self.scheduler.get_job(job_id)
        self.assertTrue(job["metadata"].get("is_research"))
        self.assertEqual(job["metadata"].get("topic"), "Transformer Attention Mechanisms")

        # Disable and verify it doesn't run
        self.scheduler.disable(job_id)
        res = self.scheduler.tick(current_time=time.time() + 7200.0)
        self.assertEqual(len(res), 0)


class TestProgressMonitoring(unittest.TestCase):
    """Capability 106: Progress Monitoring"""

    def setUp(self):
        self.monitor = ProgressMonitor(workflow_name="DeployRelease")
        self.monitor.register_task("build", weight=2.0)
        self.monitor.register_task("test", weight=3.0)
        self.monitor.register_task("deploy", weight=5.0)
        self.monitor.add_milestone("m_qa", "QA Verified", ["build", "test"])

    def test_weighted_progress_and_milestones(self):
        # Initial
        self.assertEqual(self.monitor.get_completion_percentage(), 0.0)

        # Build complete (weight 2.0 / 10.0 = 20%)
        self.monitor.update_task("build", 1.0, status="COMPLETED")
        self.assertEqual(self.monitor.get_completion_percentage(), 20.0)
        self.assertFalse(self.monitor.milestones["m_qa"].completed)

        # Test complete (weight 3.0 / 10.0 = +30% -> 50%)
        summary = self.monitor.update_task("test", 1.0, status="COMPLETED")
        self.assertEqual(self.monitor.get_completion_percentage(), 50.0)
        self.assertTrue(self.monitor.milestones["m_qa"].completed)
        self.assertIn("m_qa", summary["newly_achieved_milestones"])


class TestFailureRecovery(unittest.TestCase):
    """Capability 107: Failure Recovery"""

    def setUp(self):
        self.recovery = FailureRecoveryManager()

    def test_error_classification(self):
        self.assertEqual(classify_error(TimeoutError("Socket timed out")), ErrorCategory.TRANSIENT)
        self.assertEqual(classify_error(TypeError("unsupported operand type")), ErrorCategory.PERMANENT)
        self.assertEqual(classify_error(FileNotFoundError("No such file")), ErrorCategory.RESOURCE)

    def test_retry_with_success_on_retry(self):
        attempts = {"count": 0}

        def flaky_service():
            attempts["count"] += 1
            if attempts["count"] < 2:
                raise ConnectionResetError("Temporary blip")
            return "recovered"

        res = self.recovery.execute_with_resilience(
            action_name="flaky_call",
            fn=flaky_service,
            retry_policy=RetryPolicy(max_retries=3, base_delay_seconds=0.01)
        )
        self.assertEqual(res, "recovered")
        self.assertEqual(attempts["count"], 2)

    def test_circuit_breaker_tripping_and_fallback(self):
        cb = self.recovery.get_circuit_breaker("fragile_api", threshold=2, timeout=0.1)

        def failing_action():
            raise TimeoutError("Endpoint down")

        def fallback_action():
            return "cached_payload"

        # First failure
        with self.assertRaises(TimeoutError):
            self.recovery.execute_with_resilience("call_1", failing_action, retry_policy=RetryPolicy(max_retries=0), cb_name="fragile_api")

        # Second failure trips breaker
        with self.assertRaises(TimeoutError):
            self.recovery.execute_with_resilience("call_2", failing_action, retry_policy=RetryPolicy(max_retries=0), cb_name="fragile_api")

        self.assertEqual(cb.state, CircuitState.OPEN)

        # Call with fallback passes immediately without invoking failing action
        res = self.recovery.execute_with_resilience(
            "call_3", failing_action, fallback_fn=fallback_action, cb_name="fragile_api"
        )
        self.assertEqual(res, "cached_payload")


class TestSelfDiagnostics(unittest.TestCase):
    """Capability 108: Self-Diagnostics"""

    def setUp(self):
        self.diag = SelfDiagnostics()

    def test_run_diagnostics(self):
        report = self.diag.run_all_checks()
        self.assertIsInstance(report, HealthReport)
        self.assertGreater(report.health_score, 0)
        self.assertIn(report.overall_status, ["HEALTHY", "DEGRADED", "CRITICAL"])

        check_ids = [c.check_id for c in report.checks]
        self.assertIn("py_version", check_ids)
        self.assertIn("config_valid", check_ids)
        self.assertIn("disk_space", check_ids)


class TestSelfTesting(unittest.TestCase):
    """Capability 109: Self-Testing"""

    def setUp(self):
        self.tester = SelfTestRunner()

    def test_smoke_tests_suite(self):
        summary = self.tester.run_smoke_tests()
        self.assertIsInstance(summary, TestSummary)
        self.assertEqual(summary.total, 4)
        self.assertEqual(summary.failed, 0)
        self.assertEqual(summary.errors, 0)
        self.assertEqual(summary.pass_rate, 1.0)

        md = summary.to_markdown()
        self.assertIn("# Self-Test Execution Summary", md)
        self.assertIn("PASSED", md)


class TestWorkflowOptimization(unittest.TestCase):
    """Capability 110: Workflow Optimization"""

    def setUp(self):
        self.optimizer = WorkflowOptimizer()

    def test_optimization_analysis(self):
        dag = TaskDAG()
        dag.add_task(TaskNode(id="A", title="Data Ingestion", duration_estimate_seconds=20))
        dag.add_task(TaskNode(id="B1", title="Feature Extraction", dependencies=["A"], duration_estimate_seconds=30))
        dag.add_task(TaskNode(id="B2", title="Metadata Tagging", dependencies=["A"], duration_estimate_seconds=30))
        # Add a bottleneck task
        dag.add_task(TaskNode(id="C", title="Heavy Model Training", dependencies=["B1", "B2"], duration_estimate_seconds=120))

        report = self.optimizer.optimize_dag(dag)
        self.assertEqual(report.original_sequential_seconds, 200)
        self.assertEqual(report.parallel_critical_path_seconds, 170)
        self.assertGreaterEqual(report.speedup_factor, 1.0)
        self.assertIn("C", report.bottleneck_tasks)

        # Check suggestions
        types = [s.suggestion_type for s in report.suggestions]
        self.assertIn("BOTTLENECK_SPLIT", types)
        self.assertIn("PARALLELIZE", types)


class TestContextualRecommendations(unittest.TestCase):
    """Capability 111: Contextual Recommendations"""

    def setUp(self):
        self.recommender = ContextualRecommender()

    def test_recommendation_generation(self):
        context = {
            "recent_errors": ["ConnectionRefusedError on port 5432"],
            "has_uncommitted_changes": True,
            "cpu_percent": 88.0,
            "ram_percent": 82.0,
            "new_notes_count": 3,
            "untested_code_changes": True
        }
        recs = self.recommender.evaluate_context(context)
        self.assertGreaterEqual(len(recs), 4)

        categories = {r.category for r in recs}
        self.assertIn("SAFETY", categories)
        self.assertIn("PERFORMANCE", categories)
        self.assertIn("KNOWLEDGE", categories)
        self.assertIn("CODE", categories)


class TestEventMonitoring(unittest.TestCase):
    """Capability 112: Event Monitoring"""

    def setUp(self):
        self.bus = AutonomousEventBus()

    def test_event_publish_and_wildcard_subscription(self):
        received_task_events = []
        received_all_events = []

        self.bus.subscribe("task.*", lambda ev: received_task_events.append(ev))
        self.bus.subscribe("*", lambda ev: received_all_events.append(ev))

        self.bus.publish("task.started", source="worker", payload={"task_id": "T1"})
        self.bus.publish("task.completed", source="worker", payload={"task_id": "T1"})
        self.bus.publish("system.alert", source="guard", payload={"level": "warn"})

        self.assertEqual(len(received_task_events), 2)
        self.assertEqual(len(received_all_events), 3)

        history = self.bus.get_history("task.*")
        self.assertEqual(len(history), 2)


class TestTaskContinuity(unittest.TestCase):
    """Capability 113: Task Continuity (Checkpoint & State Resumption)"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cp_manager = CheckpointManager(storage_dir=pathlib.Path(self.temp_dir))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_checkpoint_save_and_restore(self):
        dag = TaskDAG()
        dag.add_task(TaskNode(id="step_1", title="Step 1", duration_estimate_seconds=10))
        dag.add_task(TaskNode(id="step_2", title="Step 2", dependencies=["step_1"], duration_estimate_seconds=15))

        completed = {"step_1"}
        outputs = {"step_1": {"data": "processed"}}

        cid = self.cp_manager.save_checkpoint("wf_alpha", dag, completed, outputs)
        self.assertTrue(cid.startswith("chk_wf_alpha_"))

        # Verify integrity load
        rec = self.cp_manager.load_checkpoint(cid)
        self.assertEqual(rec.workflow_id, "wf_alpha")
        self.assertEqual(rec.completed_task_ids, ["step_1"])

        # Restore execution
        restored_dag, restored_completed, restored_outputs = self.cp_manager.restore_execution(cid)
        self.assertIn("step_1", restored_completed)
        self.assertEqual(restored_dag.tasks["step_1"].status, TaskStatus.COMPLETED)
        self.assertEqual(restored_outputs["step_1"], {"data": "processed"})


class TestResourceAwareness(unittest.TestCase):
    """Capability 114: Resource Awareness & Throttling"""

    def setUp(self):
        self.guard = ResourceGuard()

    def test_sample_and_metrics(self):
        metrics = self.guard.sample()
        self.assertIsInstance(metrics, ResourceMetrics)
        self.assertGreaterEqual(metrics.cpu_percent, 0.0)
        self.assertGreaterEqual(metrics.memory_percent, 0.0)

    def test_throttle_modes(self):
        # Normal
        m_normal = ResourceMetrics(cpu_percent=20.0, memory_percent=40.0, memory_available_mb=4000.0, disk_percent=50.0)
        self.assertEqual(self.guard.get_throttle_level(m_normal), ThrottleLevel.NORMAL)

        # Moderate
        m_mod = ResourceMetrics(cpu_percent=78.0, memory_percent=60.0, memory_available_mb=2000.0, disk_percent=50.0)
        self.assertEqual(self.guard.get_throttle_level(m_mod), ThrottleLevel.MODERATE)

        # Aggressive
        m_agg = ResourceMetrics(cpu_percent=88.0, memory_percent=70.0, memory_available_mb=1000.0, disk_percent=50.0)
        self.assertEqual(self.guard.get_throttle_level(m_agg), ThrottleLevel.AGGRESSIVE)

        # Paused
        m_pause = ResourceMetrics(cpu_percent=96.0, memory_percent=96.0, memory_available_mb=200.0, disk_percent=95.0)
        self.assertEqual(self.guard.get_throttle_level(m_pause), ThrottleLevel.PAUSED)


class TestAutonomousDocumentation(unittest.TestCase):
    """Capability 115: Autonomous Documentation"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.doc = AutonomousDocumenter(notes_dir=pathlib.Path(self.temp_dir))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_execution_report_and_mermaid(self):
        dag = TaskDAG()
        dag.add_task(TaskNode(id="P1", title="Parse Data", status=TaskStatus.COMPLETED))
        dag.add_task(TaskNode(id="P2", title="Generate Graph", dependencies=["P1"], status=TaskStatus.COMPLETED))

        report_md = self.doc.generate_execution_report("GraphBuild", dag, {"actual_duration_seconds": 12.5})
        self.assertIn("flowchart TD", report_md)
        self.assertIn("P1", report_md)
        self.assertIn("Parse Data [Done]", report_md)
        self.assertIn("## Task Breakdown", report_md)

        # Post-mortem test
        pm_md = self.doc.generate_post_mortem("BuildService", "P2", "MemoryError: OOM", [{"action": "retry", "outcome": "failed", "detail": "OOM"}])
        self.assertIn("# Incident Post-Mortem", pm_md)
        self.assertIn("MemoryError: OOM", pm_md)

        # Save report
        path = self.doc.save_report("TestRun", report_md)
        self.assertTrue(path.exists())


class TestAutonomousEngineIntegration(unittest.TestCase):
    """End-to-End Integration of AutonomousEngine"""

    def setUp(self):
        self.engine = AutonomousEngine()

    def tearDown(self):
        self.engine.shutdown()

    def test_capabilities_catalogue_completeness(self):
        for cap_id in range(101, 116):
            self.assertIn(cap_id, CAPABILITIES_MAP)
            self.assertTrue(issubclass(CAPABILITIES_MAP[cap_id]["class"], object))

    def test_e2e_decompose_plan_and_execute(self):
        # 1. Decompose & Plan
        decomp, plan = self.engine.decompose_and_plan("Build an automated test reporter for Python")
        self.assertGreater(len(plan.dag.tasks), 0)

        # 2. Execute plan with simulated executors
        summary = self.engine.execute_dag(plan.dag, workflow_id="wf_e2e_test")
        self.assertEqual(summary["status"], "COMPLETED")
        self.assertEqual(len(summary["completed_tasks"]), len(plan.dag.tasks))
        self.assertIn("final_checkpoint_id", summary)

        # 3. Resume from checkpoint
        resume_summary = self.engine.resume_workflow(summary["final_checkpoint_id"])
        self.assertEqual(resume_summary["status"], "COMPLETED")

    def test_handler_dispatch(self):
        from jarvis.skills.handlers import dispatch_skill
        res_decomp = dispatch_skill("goal_decomposition", {"goal": "Build a REST API in Python"})
        self.assertEqual(res_decomp["status"], "success")
        self.assertIn("decomposed_goal", res_decomp)

        res_diag = dispatch_skill("self_diagnostics", {})
        self.assertEqual(res_diag["status"], "success")
        self.assertIn("diagnostics", res_diag)

        res_opt = dispatch_skill("workflow_optimization", {"goal": "Pipeline data"})
        self.assertEqual(res_opt["status"], "success")
        self.assertIn("optimization_report", res_opt)


if __name__ == "__main__":
    unittest.main()
